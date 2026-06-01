#!/usr/bin/env python3
"""Weekly MA pullback monitor for a curated Futu watchlist.

Default data order is Futu OpenD first, then Nasdaq public history for US-listed
fallbacks. The monitor keeps running when one symbol/source fails so one noisy
ticker does not block the whole radar.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import logging
import math
import os
import socket
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


NASDAQ_HIST_URL = "https://api.nasdaq.com/api/quote/{symbol}/historical"
NASDAQ_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/",
}
FUTU_DEFAULT_HOST = "127.0.0.1"
FUTU_DEFAULT_PORT = 11111

MA_PERIODS = (5, 10, 20, 30, 60, 120, 250)
DEFAULT_WATCH_MAS = (10, 20, 30, 60, 120)
CROSS_PAIRS = ((5, 10), (10, 20), (20, 30), (30, 60))
FUTU_PORT_CACHE: Dict[Tuple[str, int], bool] = {}


class DataError(RuntimeError):
    pass


@dataclass
class Bar:
    date: dt.date
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


def parse_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {"--", "N/A", "NaN"}:
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()").replace("$", "").replace(",", "").replace("%", "")
    try:
        number = float(text)
    except ValueError:
        return None
    return -number if negative else number


def parse_date(value: str) -> dt.date:
    return dt.datetime.strptime(value, "%m/%d/%Y").date()


def mean(values: Iterable[float]) -> Optional[float]:
    items = [v for v in values if v is not None and not math.isnan(v)]
    if not items:
        return None
    return sum(items) / len(items)


def pct(value: Optional[float]) -> str:
    if value is None or math.isnan(value):
        return "-"
    return f"{value * 100:.1f}%"


def money(value: Optional[float]) -> str:
    if value is None or math.isnan(value):
        return "-"
    if abs(value) >= 1000:
        return f"{value:,.2f}"
    if abs(value) >= 10:
        return f"{value:.2f}"
    return f"{value:.3f}"


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def business_days_between(start: dt.date, end: dt.date) -> int:
    if end <= start:
        return 0
    days = 0
    current = start + dt.timedelta(days=1)
    while current <= end:
        if current.weekday() < 5:
            days += 1
        current += dt.timedelta(days=1)
    return days


def is_non_stock_context(item: Dict[str, Any]) -> bool:
    role = item.get("role")
    return bool(
        item.get("exclude_from_stock_radar")
        or item.get("assetclass") == "index"
        or role in {"market_filter", "hedge", "leveraged"}
    )


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def check_tcp_port(host: str, port: int, timeout: float = 1.0) -> bool:
    key = (host, port)
    if key in FUTU_PORT_CACHE:
        return FUTU_PORT_CACHE[key]
    try:
        with socket.create_connection((host, port), timeout=timeout):
            FUTU_PORT_CACHE[key] = True
            return True
    except OSError:
        FUTU_PORT_CACHE[key] = False
        return False


@contextlib.contextmanager
def suppress_futu_output():
    if truthy(os.getenv("FUTU_VERBOSE")):
        yield
        return
    previous_disable = logging.root.manager.disable
    with open(os.devnull, "w", encoding="utf-8") as devnull:
        try:
            logging.disable(logging.CRITICAL)
            with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
                yield
        finally:
            logging.disable(previous_disable)


def configure_futu_logging() -> None:
    if truthy(os.getenv("FUTU_VERBOSE")):
        return
    try:
        from futu import logger, set_futu_debug_model  # type: ignore

        set_futu_debug_model(False)
        logger.console_level = logging.WARNING
        logger.enable_console_log(False)
    except Exception:
        pass


def fetch_nasdaq_history(
    symbol: str,
    assetclass: str = "stocks",
    years: int = 7,
    limit: int = 5000,
    retries: int = 2,
) -> List[Bar]:
    today = dt.date.today()
    start = today - dt.timedelta(days=365 * years + 30)
    params = {
        "assetclass": assetclass,
        "fromdate": start.isoformat(),
        "todate": today.isoformat(),
        "limit": str(limit),
    }
    url = NASDAQ_HIST_URL.format(symbol=urllib.parse.quote(symbol.upper()))
    url = f"{url}?{urllib.parse.urlencode(params)}"

    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(url, headers=NASDAQ_HEADERS)
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            status = payload.get("status") or {}
            if status.get("rCode") != 200 or not payload.get("data"):
                message = status.get("bCodeMessage") or payload.get("message")
                raise DataError(f"Nasdaq returned no data: {message}")
            rows = (((payload["data"] or {}).get("tradesTable") or {}).get("rows") or [])
            bars: List[Bar] = []
            for row in rows:
                close = parse_number(row.get("close"))
                open_ = parse_number(row.get("open"))
                high = parse_number(row.get("high"))
                low = parse_number(row.get("low"))
                if None in (close, open_, high, low):
                    continue
                bars.append(
                    Bar(
                        date=parse_date(row["date"]),
                        open=float(open_),
                        high=float(high),
                        low=float(low),
                        close=float(close),
                        volume=float(parse_number(row.get("volume")) or 0),
                    )
                )
            bars.sort(key=lambda bar: bar.date)
            if len(bars) < 5:
                raise DataError(f"only {len(bars)} usable daily bars")
            return bars
        except Exception as exc:  # noqa: BLE001 - report source failures compactly.
            last_error = exc
            if attempt < retries:
                time.sleep(0.8 * (attempt + 1))
    raise DataError(str(last_error))


def parse_isoish_date(value: Any) -> dt.date:
    text = str(value).strip()
    if " " in text:
        text = text.split(" ", 1)[0]
    return dt.date.fromisoformat(text)


def futu_quote_code(item: Dict[str, Any], symbol: str) -> str:
    if item.get("futu_code"):
        return str(item["futu_code"]).upper()
    source_symbol = str(item.get("source_symbol") or symbol).upper().lstrip(".")
    if "." in source_symbol and source_symbol.split(".", 1)[0] in {"US", "HK", "SH", "SZ"}:
        return source_symbol
    market = str(item.get("futu_market") or os.getenv("FUTU_MARKET") or "US").upper()
    return f"{market}.{source_symbol}"


def futu_market_prefix(item: Dict[str, Any], symbol: str) -> str:
    code = futu_quote_code(item, symbol)
    if "." in code:
        return code.split(".", 1)[0].upper()
    return str(item.get("futu_market") or os.getenv("FUTU_MARKET") or "US").upper()


def has_nasdaq_fallback(item: Dict[str, Any]) -> bool:
    if item.get("nasdaq_fallback") is False:
        return False
    symbol = str(item.get("symbol", "")).upper()
    market = futu_market_prefix(item, symbol)
    if market != "US":
        return False
    return item.get("assetclass", "stocks") in {"stocks", "etf", "index"}


def fetch_futu_history(
    item: Dict[str, Any],
    years: int = 7,
    min_bars: int = 30,
) -> List[Bar]:
    try:
        from futu import AuType, KLType, OpenQuoteContext, RET_OK  # type: ignore
    except Exception as exc:  # noqa: BLE001 - optional dependency.
        raise DataError("futu-api is not installed; run `python3 -m pip install futu-api` first") from exc

    configure_futu_logging()
    symbol = item["symbol"].upper()
    code = futu_quote_code(item, symbol)
    host = str(item.get("futu_host") or os.getenv("FUTU_OPEND_HOST") or FUTU_DEFAULT_HOST)
    port = int(item.get("futu_port") or os.getenv("FUTU_OPEND_PORT") or FUTU_DEFAULT_PORT)
    if not check_tcp_port(host, port):
        raise DataError(f"FutuOpenD is not reachable at {host}:{port}")
    today = dt.date.today()
    start = today - dt.timedelta(days=365 * years + 30)
    quote_ctx = None
    bars: List[Bar] = []
    page_req_key = None
    try:
        with suppress_futu_output():
            quote_ctx = OpenQuoteContext(host=host, port=port)
            while True:
                ret, data, page_req_key = quote_ctx.request_history_kline(
                    code,
                    start=start.isoformat(),
                    end=today.isoformat(),
                    ktype=KLType.K_DAY,
                    autype=AuType.QFQ,
                    max_count=1000,
                    page_req_key=page_req_key,
                )
                if ret != RET_OK:
                    raise DataError(f"Futu returned no data for {code}: {data}")
                if data is None or len(data) == 0:
                    break
                for _, row in data.iterrows():
                    try:
                        bars.append(
                            Bar(
                                date=parse_isoish_date(row["time_key"]),
                                open=float(row["open"]),
                                high=float(row["high"]),
                                low=float(row["low"]),
                                close=float(row["close"]),
                                volume=float(row.get("volume", 0) or 0),
                            )
                        )
                    except Exception:
                        continue
                if page_req_key is None:
                    break
    finally:
        if quote_ctx is not None:
            with suppress_futu_output():
                quote_ctx.close()
                time.sleep(0.2)

    bars.sort(key=lambda bar: bar.date)
    deduped: List[Bar] = []
    for bar in bars:
        if deduped and deduped[-1].date == bar.date:
            deduped[-1] = bar
        else:
            deduped.append(bar)
    if len(deduped) < min(min_bars, 5):
        raise DataError(f"Futu {code} only has {len(deduped)} usable daily bars")
    return deduped


def provider_order(provider: str, item: Optional[Dict[str, Any]] = None) -> List[str]:
    if provider == "auto":
        if item is not None and has_nasdaq_fallback(item):
            return ["futu", "nasdaq"]
        return ["futu"]
    return [provider]


def fetch_history(item: Dict[str, Any], years: int, provider: str) -> Tuple[List[Bar], str, str]:
    errors: List[str] = []
    for candidate in provider_order(provider, item):
        try:
            if candidate == "nasdaq":
                symbol = str(item.get("source_symbol") or item["symbol"]).upper()
                bars = fetch_nasdaq_history(symbol, assetclass=item.get("assetclass", "stocks"), years=years)
                warning = f"fallback_after:{'; '.join(errors)}" if errors else ""
                return bars, "nasdaq", warning
            if candidate == "futu":
                return fetch_futu_history(item, years=years), "futu", ""
            errors.append(f"{candidate}: unknown provider")
        except Exception as exc:  # noqa: BLE001 - try the next provider and report all failures.
            errors.append(f"{candidate}: {exc}")
    raise DataError("; ".join(errors))


def resample_weekly(daily: List[Bar]) -> List[Dict[str, Any]]:
    weeks: Dict[dt.date, Dict[str, Any]] = {}
    for bar in daily:
        week_start = bar.date - dt.timedelta(days=bar.date.weekday())
        current = weeks.get(week_start)
        if current is None:
            weeks[week_start] = {
                "date": bar.date,
                "week_start": week_start,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            continue
        current["date"] = bar.date
        current["high"] = max(current["high"], bar.high)
        current["low"] = min(current["low"], bar.low)
        current["close"] = bar.close
        current["volume"] += bar.volume
    return [weeks[key] for key in sorted(weeks)]


def add_indicators(weekly: List[Dict[str, Any]]) -> None:
    closes: List[float] = []
    true_ranges: List[float] = []
    prev_close: Optional[float] = None
    for index, bar in enumerate(weekly):
        closes.append(bar["close"])
        for period in MA_PERIODS:
            if len(closes) >= period:
                bar[f"ma{period}"] = sum(closes[-period:]) / period
            else:
                bar[f"ma{period}"] = None
        if prev_close is None:
            tr = bar["high"] - bar["low"]
        else:
            tr = max(
                bar["high"] - bar["low"],
                abs(bar["high"] - prev_close),
                abs(bar["low"] - prev_close),
            )
        true_ranges.append(tr)
        bar["atr14"] = mean(true_ranges[-14:]) if len(true_ranges) >= 3 else None
        if index >= 4:
            for period in MA_PERIODS:
                now = bar.get(f"ma{period}")
                old = weekly[index - 4].get(f"ma{period}")
                bar[f"ma{period}_slope4"] = (now - old) / old if now and old else None
        prev_close = bar["close"]


def recent_cross_age(
    weekly: List[Dict[str, Any]], short_period: int, long_period: int, max_weeks: int = 8
) -> Optional[int]:
    short_key = f"ma{short_period}"
    long_key = f"ma{long_period}"
    for age in range(max_weeks + 1):
        idx = len(weekly) - 1 - age
        if idx <= 0:
            continue
        now_short = weekly[idx].get(short_key)
        now_long = weekly[idx].get(long_key)
        prev_short = weekly[idx - 1].get(short_key)
        prev_long = weekly[idx - 1].get(long_key)
        if None in (now_short, now_long, prev_short, prev_long):
            continue
        if prev_short <= prev_long and now_short > now_long:
            return age
    return None


def infer_buffer(latest: Dict[str, Any], item: Dict[str, Any]) -> float:
    if item.get("buffer_pct") is not None:
        return float(item["buffer_pct"])
    close = latest["close"]
    atr_pct = (latest.get("atr14") or 0) / close if close else 0
    risk = item.get("risk", "medium")
    floor = 0.035 if risk in {"high", "very_high"} else 0.025
    ceiling = 0.085 if risk in {"high", "very_high"} else 0.06
    return clamp(max(floor, 0.35 * atr_pct), floor, ceiling)


def trend_state(latest: Dict[str, Any]) -> Tuple[str, float]:
    close = latest["close"]
    ma20 = latest.get("ma20")
    ma30 = latest.get("ma30")
    ma60 = latest.get("ma60")
    slope30 = latest.get("ma30_slope4") or 0
    slope60 = latest.get("ma60_slope4") or 0
    score = 2.0
    if ma20 and ma30 and close > ma20 > ma30:
        score += 1.0
    if ma30 and ma60 and ma30 > ma60:
        score += 0.8
    if slope30 > 0:
        score += 0.7
    if slope60 > 0:
        score += 0.5
    if ma60 and close < ma60:
        score -= 1.0
    if ma30 and close < ma30:
        score -= 0.5
    if score >= 4.3:
        return "strong_uptrend", score
    if score >= 3.2:
        return "constructive", score
    if score >= 2.2:
        return "base_or_mixed", score
    return "weak", score


def evaluate_symbol(item: Dict[str, Any], years: int, provider: str) -> Dict[str, Any]:
    symbol = item["symbol"].upper()
    source_symbol = item.get("source_symbol", symbol).upper()
    assetclass = item.get("assetclass", "stocks")
    context_only = is_non_stock_context(item)
    daily, data_provider, provider_warning = fetch_history(item, years=years, provider=provider)
    history_warnings: List[str] = []
    if provider_warning:
        history_warnings.append(provider_warning)
    if len(daily) < 30:
        history_warnings.append(f"short_history:{len(daily)} daily bars")
    history_warning = "; ".join(history_warnings)
    weekly = resample_weekly(daily)
    add_indicators(weekly)
    latest = weekly[-1]
    close = latest["close"]
    low = latest["low"]
    buffer = infer_buffer(latest, item)
    trend, trend_score = trend_state(latest)
    watch_mas = item.get("watch_mas") or list(DEFAULT_WATCH_MAS)

    pure_hits: List[Dict[str, Any]] = []
    levels: List[Dict[str, Any]] = []
    for period in watch_mas:
        ma_value = latest.get(f"ma{period}")
        if not ma_value:
            continue
        distance = (close - ma_value) / ma_value
        alert_price = ma_value * (1 + buffer)
        broke_badly = close < ma_value * (1 - 1.25 * buffer)
        close_still_near = close <= ma_value * (1 + max(buffer * 3.0, 0.10))
        touched = low <= alert_price and close_still_near and not broke_badly
        near_close = -buffer <= distance <= buffer * 1.5
        levels.append(
            {
                "ma": period,
                "value": ma_value,
                "distance": distance,
                "alert_price": alert_price,
                "touched": touched,
                "near_close": near_close,
            }
        )
        if touched or near_close:
            pure_hits.append(
                {
                    "kind": "pure_pullback",
                    "ma": period,
                    "support": ma_value,
                    "distance": distance,
                    "reason": f"price is {pct(distance)} from MA{period}",
                }
            )

    recent_crosses = []
    for short_period, long_period in CROSS_PAIRS:
        age = recent_cross_age(weekly, short_period, long_period, max_weeks=8)
        if age is not None:
            recent_crosses.append((short_period, long_period, age))

    cross_hit: Optional[Dict[str, Any]] = None
    core_mas = [latest.get("ma10"), latest.get("ma20"), latest.get("ma30")]
    core_mas = [value for value in core_mas if value]
    if recent_crosses and core_mas:
        upper_core = max(core_mas)
        lower_core = min(core_mas)
        spread = (upper_core - lower_core) / upper_core if upper_core else None
        distance_to_upper = (close - upper_core) / upper_core
        touched_upper = low <= upper_core * (1 + buffer * 1.8)
        held_upper = close >= upper_core * (1 - buffer)
        close_in_add_zone = -buffer <= distance_to_upper <= max(buffer * 2.2, 0.055)
        still_near_after_touch = close <= upper_core * (1 + max(buffer * 2.6, 0.10))
        if held_upper and (close_in_add_zone or (touched_upper and still_near_after_touch)):
            cross_hit = {
                "kind": "cross_upper_add",
                "support": upper_core,
                "distance": distance_to_upper,
                "spread": spread,
                "crosses": recent_crosses,
                "reason": "recent bullish MA cross; price is near the upper MA support band",
            }

    ma20 = latest.get("ma20")
    ma30 = latest.get("ma30")
    atr_pct = ((latest.get("atr14") or 0) / close) if close else None
    extended = False
    if ma20 and close > ma20 * (1 + max(0.18, 2.0 * (atr_pct or 0))):
        extended = True
    if ma30 and close > ma30 * (1 + max(0.25, 2.4 * (atr_pct or 0))):
        extended = True

    signals = list(pure_hits)
    if cross_hit:
        signals.insert(0, cross_hit)

    narrative = float(item.get("narrative_score", 2.5))
    quality = float(item.get("quality_score", 2.5))
    risk = item.get("risk", "medium")
    risk_penalty = {
        "low": 0.0,
        "medium": 0.2,
        "medium_high": 0.45,
        "high": 0.75,
        "very_high": 1.1,
        "hedge": 0.7,
    }.get(risk, 0.35)

    tech_score = 0.0
    if cross_hit:
        tech_score = 5.0 if trend in {"strong_uptrend", "constructive"} else 4.0
    elif pure_hits:
        tech_score = 4.2 if trend in {"strong_uptrend", "constructive"} else 3.2
    elif extended:
        tech_score = 1.5
    else:
        tech_score = min(2.5, trend_score)

    composite = 0.45 * tech_score + 0.30 * narrative + 0.25 * quality - risk_penalty
    if context_only:
        signals = []
        extended = False

    active = bool(signals)
    if active and composite >= 4.1 and risk not in {"high", "very_high", "hedge"}:
        grade = "A"
    elif active and composite >= 3.55:
        grade = "B+"
    elif active and composite >= 2.85:
        grade = "B"
    elif active:
        grade = "C"
    elif context_only:
        grade = "CONTEXT"
    elif extended:
        grade = "WAIT"
    else:
        grade = "WATCH"

    next_levels = [level for level in levels if level["value"] <= close]
    next_levels.sort(key=lambda level: abs(level["distance"]))
    next_level = next_levels[0] if next_levels else (levels[0] if levels else None)

    return {
        "symbol": symbol,
        "source_symbol": source_symbol,
        "name": item.get("name", symbol),
        "assetclass": assetclass,
        "data_provider": data_provider,
        "history_daily_bars": len(daily),
        "data_warning": history_warning,
        "futu_code": futu_quote_code(item, symbol),
        "context_only": context_only,
        "themes": item.get("themes", []),
        "role": item.get("role", "watch"),
        "risk": risk,
        "narrative_score": narrative,
        "quality_score": quality,
        "latest_date": latest["date"].isoformat(),
        "close": close,
        "weekly_low": low,
        "weekly_high": latest["high"],
        "atr_pct": atr_pct,
        "buffer_pct": buffer,
        "trend": trend,
        "trend_score": trend_score,
        "signals": signals,
        "levels": levels,
        "next_level": next_level,
        "recent_crosses": recent_crosses,
        "extended": extended,
        "composite": composite,
        "grade": grade,
        "notes": item.get("notes", ""),
    }


def signal_label(signal: Dict[str, Any]) -> str:
    if signal["kind"] == "cross_upper_add":
        crosses = ", ".join(f"MA{s}>{l}({age}w)" for s, l, age in signal["crosses"])
        return f"交叉后上沿加仓区 / {crosses}"
    if signal["kind"] == "pure_pullback":
        return f"单纯回踩 MA{signal['ma']}"
    return signal["kind"]


def action_text(result: Dict[str, Any]) -> str:
    if result["grade"] == "CONTEXT":
        return "市场/杠杆产品参考项，不进入普通个股加仓评分。"
    if result["grade"] == "A":
        return "优先提醒：技术到位且叙事/基本面层可接受，适合进入人工复核。"
    if result["grade"] in {"B+", "B"}:
        return "观察提醒：技术到位，但仓位/事件/估值需要再确认。"
    if result["grade"] == "C":
        return "只做雷达：偏交易或高风险，不自动升优先级。"
    if result["grade"] == "WAIT":
        return "离均线偏远，等回踩；不追高。"
    return "未到位，继续等下一条 MA 支撑线。"


def compact_reason(result: Dict[str, Any]) -> str:
    parts = []
    if result["signals"]:
        parts.append(signal_label(result["signals"][0]))
    parts.append(result["trend"])
    if result["themes"]:
        parts.append("/".join(result["themes"][:2]))
    if result["notes"]:
        parts.append(result["notes"])
    return "; ".join(parts)


def load_state(path: Optional[str]) -> Dict[str, Any]:
    if not path or not os.path.exists(path):
        return {"alerts": {}}
    try:
        with open(path, "r", encoding="utf-8") as file:
            payload = json.load(file)
        if isinstance(payload, dict):
            payload.setdefault("alerts", {})
            return payload
    except Exception:
        pass
    return {"alerts": {}}


def save_state(path: Optional[str], state: Dict[str, Any]) -> None:
    if not path:
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2, sort_keys=True, default=str)


def grade_rank(grade: str) -> int:
    return {"A": 5, "B+": 4, "B": 3, "C": 2, "WAIT": 1, "WATCH": 0}.get(grade, 0)


def primary_signal_key(result: Dict[str, Any]) -> Optional[str]:
    if not result["signals"]:
        return None
    signal = result["signals"][0]
    if signal["kind"] == "pure_pullback":
        return f"{result['symbol']}:PURE_PULLBACK:MA{signal['ma']}"
    if signal["kind"] == "cross_upper_add":
        return f"{result['symbol']}:CROSS_RETEST_ADD"
    return f"{result['symbol']}:{signal['kind']}"


def signal_proximity(result: Dict[str, Any]) -> Optional[float]:
    if not result["signals"]:
        return None
    distance = result["signals"][0].get("distance")
    if distance is None:
        return None
    return abs(float(distance))


def apply_dedupe(results: List[Dict[str, Any]], state: Dict[str, Any], window_days: int = 5) -> None:
    alerts = state.setdefault("alerts", {})
    latest_dates = [r["latest_date"] for r in results if r.get("latest_date")]
    if latest_dates:
        state["last_market_date"] = max(latest_dates)
    state["last_checked_at"] = dt.datetime.now().isoformat(timespec="seconds")

    for result in results:
        result["suppressed"] = False
        result["dedupe_reason"] = ""
        key = primary_signal_key(result)
        if not key:
            continue

        current_date = dt.date.fromisoformat(result["latest_date"])
        current_rank = grade_rank(result["grade"])
        current_proximity = signal_proximity(result)
        prior = alerts.get(key)
        should_alert = True
        if prior:
            prior_date = dt.date.fromisoformat(prior.get("latest_date", result["latest_date"]))
            age = business_days_between(prior_date, current_date)
            prior_rank = int(prior.get("grade_rank", 0))
            prior_proximity = prior.get("proximity")
            improved_grade = current_rank > prior_rank
            improved_zone = (
                current_proximity is not None
                and prior_proximity is not None
                and (float(prior_proximity) - current_proximity) >= max(float(prior_proximity) * 0.25, 0.005)
            )
            should_alert = age >= window_days or improved_grade or improved_zone
            if not should_alert:
                result["suppressed"] = True
                result["dedupe_reason"] = f"{age}个交易日内已提醒，未进入更优区间"

        if should_alert:
            alerts[key] = {
                "symbol": result["symbol"],
                "latest_date": result["latest_date"],
                "grade": result["grade"],
                "grade_rank": current_rank,
                "proximity": current_proximity,
                "close": result["close"],
                "signal": signal_label(result["signals"][0]),
            }


def markdown_report(results: List[Dict[str, Any]], errors: List[Dict[str, str]]) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    ordinary = [r for r in results if not r.get("context_only")]
    context = [r for r in results if r.get("context_only")]
    active = [r for r in ordinary if r["signals"] and not r.get("suppressed")]
    active.sort(key=lambda r: ({"A": 0, "B+": 1, "B": 2, "C": 3}.get(r["grade"], 9), -r["composite"]))
    suppressed = [r for r in ordinary if r["signals"] and r.get("suppressed")]
    suppressed.sort(key=lambda r: -r["composite"])
    wait = [r for r in ordinary if not r["signals"] and r["extended"]]
    wait.sort(key=lambda r: -r["composite"])
    watch = [r for r in ordinary if not r["signals"] and not r["extended"]]
    watch.sort(key=lambda r: r["next_level"]["distance"] if r.get("next_level") else 99)

    lines = [
        "# 美股/ADR 周线回踩监控",
        "",
        f"- Generated: {now}",
        "- Data source: Futu OpenD first; Nasdaq public historical quote API fallback",
        "- Signal intent: alert/review only, not automatic buy or sell advice.",
        "",
        "## 今日到位",
        "",
    ]

    if active:
        lines.append("| Grade | Ticker | Close | Signal | Support | Dist | Buffer | Filter | Action |")
        lines.append("|---|---:|---:|---|---:|---:|---:|---|---|")
        for result in active:
            primary = result["signals"][0]
            support = primary.get("support")
            lines.append(
        "| {grade} | {symbol} | {close} | {signal} | {support} | {dist} | {buffer} | {filter} | {action} |".format(
                    grade=result["grade"],
                    symbol=f"{result['symbol']}({result['data_provider']})",
                    close=money(result["close"]),
                    signal=signal_label(primary),
                    support=money(support),
                    dist=pct(primary.get("distance")),
                    buffer=pct(result["buffer_pct"]),
                    filter=f"N{result['narrative_score']:.0f}/Q{result['quality_score']:.0f}/{result['risk']}",
                    action=action_text(result),
                )
            )
    else:
        lines.append("No active pullback/cross-zone signal right now.")

    lines.extend(["", "## 接近到位", ""])
    near = []
    for result in watch:
        level = result.get("next_level")
        if not level:
            continue
        distance_to_alert = (result["close"] - level["alert_price"]) / level["alert_price"]
        if distance_to_alert <= max(result["buffer_pct"] * 2.2, 0.07):
            near.append((distance_to_alert, result, level))
    near.sort(key=lambda item: item[0])
    if near:
        lines.append("| Ticker | Close | Next Alert | MA | Gap To Alert | Filter | Notes |")
        lines.append("|---|---:|---:|---:|---:|---|---|")
        for distance_to_alert, result, level in near[:25]:
            lines.append(
                "| {symbol} | {close} | {alert} | MA{ma} | {gap} | N{n:.0f}/Q{q:.0f}/{risk} | {notes} |".format(
                    symbol=f"{result['symbol']}({result['data_provider']})",
                    close=money(result["close"]),
                    alert=money(level["alert_price"]),
                    ma=level["ma"],
                    gap=pct(distance_to_alert),
                    n=result["narrative_score"],
                    q=result["quality_score"],
                    risk=result["risk"],
                    notes=compact_reason(result),
                )
            )
    else:
        lines.append("No near-zone symbols within the configured alert buffer.")

    lines.extend(["", "## 结构好但未到位 / 不追高", ""])
    if wait:
        lines.append("| Ticker | Close | Nearest MA | Dist | Filter | Note |")
        lines.append("|---|---:|---:|---:|---|---|")
        for result in wait[:20]:
            level = result.get("next_level") or {}
            lines.append(
                "| {symbol} | {close} | MA{ma} {support} | {dist} | N{n:.0f}/Q{q:.0f}/{risk} | {note} |".format(
                    symbol=f"{result['symbol']}({result['data_provider']})",
                    close=money(result["close"]),
                    ma=level.get("ma", "-"),
                    support=money(level.get("value")),
                    dist=pct(level.get("distance")),
                    n=result["narrative_score"],
                    q=result["quality_score"],
                    risk=result["risk"],
                    note="强叙事也等回踩，不追扩张段。",
                )
            )
    else:
        lines.append("No symbol is flagged as too extended.")

    lines.extend(["", "## 5个交易日内已提醒", ""])
    if suppressed:
        lines.append("| Ticker | Grade | Close | Signal | Reason |")
        lines.append("|---|---|---:|---|---|")
        for result in suppressed[:20]:
            primary = result["signals"][0]
            lines.append(
                "| {symbol} | {grade} | {close} | {signal} | {reason} |".format(
                    symbol=f"{result['symbol']}({result['data_provider']})",
                    grade=result["grade"],
                    close=money(result["close"]),
                    signal=signal_label(primary),
                    reason=result.get("dedupe_reason", "-"),
                )
            )
    else:
        lines.append("No duplicate signal suppressed.")

    lines.extend(["", "## 指数 / 杠杆 / 对冲参考", ""])
    if context:
        lines.append("| Ticker | Role | Close | Trend | Nearest MA Alert | Note |")
        lines.append("|---|---|---:|---|---:|---|")
        for result in context:
            level = result.get("next_level") or {}
            lines.append(
                "| {symbol} | {role} | {close} | {trend} | MA{ma} {alert} | {note} |".format(
                    symbol=f"{result['symbol']}({result['data_provider']})",
                    role=result["role"],
                    close=money(result["close"]),
                    trend=result["trend"],
                    ma=level.get("ma", "-"),
                    alert=money(level.get("alert_price")),
                    note=result.get("notes") or action_text(result),
                )
            )
    else:
        lines.append("No context-only symbol configured.")

    lines.extend(["", "## 回避 / 数据不足 / 备用源", ""])
    if errors:
        for error in errors:
            lines.append(f"- {error['symbol']}: {error['error']}")
    else:
        lines.append("No data issue.")
    warnings = [r for r in results if r.get("data_warning")]
    if warnings:
        lines.append("")
        lines.append("Soft data notes kept in radar:")
        for result in warnings:
            lines.append(f"- {result['symbol']}({result['data_provider']}): {result['data_warning']}")

    lines.extend(["", "## Full Radar Snapshot", ""])
    lines.append("| Ticker | Grade | Trend | Close | Next MA Alert | Cross Age | Themes |")
    lines.append("|---|---|---|---:|---:|---|---|")
    for result in results:
        level = result.get("next_level") or {}
        crosses = ", ".join(f"{s}>{l}:{age}w" for s, l, age in result["recent_crosses"]) or "-"
        lines.append(
            "| {symbol} | {grade} | {trend} | {close} | MA{ma} {alert} | {crosses} | {themes} |".format(
                symbol=f"{result['symbol']}({result['data_provider']})",
                grade=result["grade"],
                trend=result["trend"],
                close=money(result["close"]),
                ma=level.get("ma", "-"),
                alert=money(level.get("alert_price")),
                crosses=crosses,
                themes="/".join(result["themes"][:3]) or "-",
            )
        )
    lines.append("")
    return "\n".join(lines)


def load_watchlist(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataError(
            f"{path} must be JSON-compatible YAML because this monitor has no third-party YAML dependency"
        ) from exc
    items = payload.get("watchlist", payload if isinstance(payload, list) else [])
    return [item for item in items if item.get("enabled", True)]


def run(
    config: str,
    out: Optional[str],
    json_out: Optional[str],
    years: int,
    symbols: Optional[List[str]],
    state_path: Optional[str],
    no_dedupe: bool,
    provider: str,
) -> int:
    items = load_watchlist(config)
    if symbols:
        wanted = {symbol.upper() for symbol in symbols}
        items = [item for item in items if item["symbol"].upper() in wanted]

    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    for item in items:
        symbol = item["symbol"].upper()
        try:
            results.append(evaluate_symbol(item, years=years, provider=provider))
        except Exception as exc:  # noqa: BLE001 - continue the radar run.
            errors.append({"symbol": symbol, "error": str(exc)})

    state = load_state(state_path)
    if not no_dedupe:
        apply_dedupe(results, state)
        save_state(state_path, state)

    report = markdown_report(results, errors)
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as file:
            file.write(report)
    if json_out:
        os.makedirs(os.path.dirname(os.path.abspath(json_out)), exist_ok=True)
        with open(json_out, "w", encoding="utf-8") as file:
            json.dump({"results": results, "errors": errors}, file, ensure_ascii=False, indent=2, default=str)
    print(report)
    return 1 if errors and not results else 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Weekly MA pullback monitor")
    parser.add_argument("--config", default="watchlist.yml")
    parser.add_argument("--out", default="reports/latest.md")
    parser.add_argument("--json-out", default="reports/latest.json")
    parser.add_argument("--state", default="reports/state.json")
    parser.add_argument(
        "--provider",
        choices=("auto", "nasdaq", "futu"),
        default=os.getenv("MARKET_DATA_PROVIDER", "auto"),
        help="Data provider. auto tries Futu OpenD first, then Nasdaq.",
    )
    parser.add_argument("--no-dedupe", action="store_true", help="Show all active signals and do not update state.")
    parser.add_argument("--years", type=int, default=7)
    parser.add_argument("--symbols", nargs="*", help="Optional ticker subset")
    args = parser.parse_args(argv)
    return run(
        args.config,
        args.out,
        args.json_out,
        args.years,
        args.symbols,
        args.state,
        args.no_dedupe,
        args.provider,
    )


if __name__ == "__main__":
    sys.exit(main())
