# 美股/ADR 周线回踩监控

- Generated: 2026-05-10 20:54
- Data source: Nasdaq public historical quote API
- Signal intent: alert/review only, not automatic buy or sell advice.

## 今日到位

No active pullback/cross-zone signal right now.

## 接近到位

No near-zone symbols within the configured alert buffer.

## 结构好但未到位 / 不追高

No symbol is flagged as too extended.

## 5个交易日内已提醒

| Ticker | Grade | Close | Signal | Reason |
|---|---|---:|---|---|
| CCJ | A | 116.75 | 交叉后上沿加仓区 / MA5>10(2w) | 0个交易日内已提醒，未进入更优区间 |
| AGRO | B+ | 13.13 | 交叉后上沿加仓区 / MA30>60(1w) | 0个交易日内已提醒，未进入更优区间 |
| BABA | B | 140.06 | 单纯回踩 MA20 | 0个交易日内已提醒，未进入更优区间 |

## 指数 / 杠杆 / 对冲参考

No context-only symbol configured.

## 回避 / 数据不足

No data issue.

## Full Radar Snapshot

| Ticker | Grade | Trend | Close | Next MA Alert | Cross Age | Themes |
|---|---|---|---:|---:|---|---|
| AGRO | B+ | strong_uptrend | 13.13 | MA10 13.70 | 30>60:1w | agriculture/energy/value |
| BABA | B | base_or_mixed | 140.06 | MA60 143.07 | 5>10:1w | China internet/AI/cloud |
| CCJ | A | strong_uptrend | 116.75 | MA10 117.79 | 5>10:2w | uranium/nuclear/energy security |
