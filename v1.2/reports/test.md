# Weekly MA Pullback Monitor

- Generated: 2026-05-10 20:00
- Data source: Nasdaq public historical quote API
- Signal intent: alert/review only, not automatic buy or sell advice.

## Active Signals

| Grade | Ticker | Close | Signal | Support | Dist | Buffer | Filter | Action |
|---|---:|---:|---|---:|---:|---:|---|---|
| B+ | AGRO | 13.13 | 交叉后上沿加仓区 / MA30>60(1w) | 13.10 | 0.2% | 4.6% | N3/Q4/medium | 观察提醒：技术到位，但仓位/事件/估值需要再确认。 |
| B | BABA | 140.06 | 单纯回踩 MA20 | 144.64 | -3.2% | 3.0% | N4/Q4/medium_high | 观察提醒：技术到位，但仓位/事件/估值需要再确认。 |

## Next Alert Levels

No near-zone symbols within the configured alert buffer.

## Too Extended / Wait

| Ticker | Close | Nearest MA | Dist | Filter | Note |
|---|---:|---:|---:|---|---|
| GOOG | 397.05 | MA20 322.83 | 23.0% | N5/Q5/low | 强叙事也等回踩，不追扩张段。 |
| RKLB | 105.47 | MA20 76.39 | 38.1% | N5/Q3/medium_high | 强叙事也等回踩，不追扩张段。 |

## Data Issues

No data issue.

## Full Radar Snapshot

| Ticker | Grade | Trend | Close | Next MA Alert | Cross Age | Themes |
|---|---|---|---:|---:|---|---|
| GOOG | WAIT | strong_uptrend | 397.05 | MA20 330.90 | 5>10:2w, 10>20:0w | AI/cloud/mega-cap |
| RKLB | WAIT | strong_uptrend | 105.47 | MA20 79.81 | 5>10:3w | space/defense/launch |
| AGRO | B+ | strong_uptrend | 13.13 | MA10 13.70 | 30>60:1w | agriculture/energy/value |
| BABA | B | base_or_mixed | 140.06 | MA60 143.07 | 5>10:1w | China internet/AI/cloud |
