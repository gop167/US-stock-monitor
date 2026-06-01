# 美股/ADR 周线回踩监控

- Generated: 2026-05-10 23:12
- Data source: Futu OpenD first; Nasdaq public historical quote API fallback
- Signal intent: alert/review only, not automatic buy or sell advice.

## 今日到位

No active pullback/cross-zone signal right now.

## 接近到位

No near-zone symbols within the configured alert buffer.

## 结构好但未到位 / 不追高

No symbol is flagged as too extended.

## 5个交易日内已提醒

No duplicate signal suppressed.

## 指数 / 杠杆 / 对冲参考

| Ticker | Role | Close | Trend | Nearest MA Alert | Note |
|---|---|---:|---|---:|---|
| SNDQ(futu) | hedge | 7.670 | weak | MA- - | 反向杠杆ETF，不参与基本面排序，只作为风险提示。 |

## 回避 / 数据不足

No data issue.

Short-history symbols kept in radar:
- SNDQ(futu): short_history:12 daily bars

## Full Radar Snapshot

| Ticker | Grade | Trend | Close | Next MA Alert | Cross Age | Themes |
|---|---|---|---:|---:|---|---|
| SNDQ(futu) | CONTEXT | weak | 7.670 | MA- - | - | inverse ETF/hedge/semiconductor |
