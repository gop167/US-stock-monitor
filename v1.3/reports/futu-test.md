# 美股/ADR 周线回踩监控

- Generated: 2026-05-10 23:21
- Data source: Futu OpenD first; Nasdaq public historical quote API fallback
- Signal intent: alert/review only, not automatic buy or sell advice.

## 今日到位

| Grade | Ticker | Close | Signal | Support | Dist | Buffer | Filter | Action |
|---|---:|---:|---|---:|---:|---:|---|---|
| B+ | AGRO(futu) | 13.13 | 交叉后上沿加仓区 / MA30>60(2w) | 13.00 | 1.0% | 4.6% | N3/Q4/medium | 观察提醒：技术到位，但仓位/事件/估值需要再确认。 |
| B | BABA(futu) | 140.06 | 单纯回踩 MA20 | 144.64 | -3.2% | 3.0% | N4/Q4/medium_high | 观察提醒：技术到位，但仓位/事件/估值需要再确认。 |

## 接近到位

No near-zone symbols within the configured alert buffer.

## 结构好但未到位 / 不追高

| Ticker | Close | Nearest MA | Dist | Filter | Note |
|---|---:|---:|---:|---|---|
| GOOG(futu) | 397.05 | MA20 322.71 | 23.0% | N5/Q5/low | 强叙事也等回踩，不追扩张段。 |
| RKLB(futu) | 105.47 | MA20 76.39 | 38.1% | N5/Q3/medium_high | 强叙事也等回踩，不追扩张段。 |

## 5个交易日内已提醒

No duplicate signal suppressed.

## 指数 / 杠杆 / 对冲参考

No context-only symbol configured.

## 回避 / 数据不足

No data issue.

## Full Radar Snapshot

| Ticker | Grade | Trend | Close | Next MA Alert | Cross Age | Themes |
|---|---|---|---:|---:|---|---|
| GOOG(futu) | WAIT | strong_uptrend | 397.05 | MA20 330.78 | 5>10:2w, 10>20:0w | AI/cloud/mega-cap |
| RKLB(futu) | WAIT | strong_uptrend | 105.47 | MA20 79.81 | 5>10:3w | space/defense/launch |
| AGRO(futu) | B+ | strong_uptrend | 13.13 | MA10 13.59 | 30>60:2w | agriculture/energy/value |
| BABA(futu) | B | base_or_mixed | 140.06 | MA60 142.65 | 5>10:1w | China internet/AI/cloud |
