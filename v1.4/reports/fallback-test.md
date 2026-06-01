# 美股/ADR 周线回踩监控

- Generated: 2026-05-11 08:03
- Data source: Futu OpenD first; Nasdaq public historical quote API fallback
- Signal intent: alert/review only, not automatic buy or sell advice.

## 今日到位

| Grade | Ticker | Close | Signal | Support | Dist | Buffer | Filter | Action |
|---|---:|---:|---|---:|---:|---:|---|---|
| A | NATKY(nasdaq) | 80.00 | 交叉后上沿加仓区 / MA5>10(3w) | 81.18 | -1.5% | 2.5% | N5/Q4/medium_high | 优先提醒：技术到位且叙事/基本面层可接受，适合进入人工复核。 |
| C | NNOMF(nasdaq) | 0.693 | 单纯回踩 MA10 | 0.663 | 4.5% | 4.4% | N3/Q2/high | 只做雷达：偏交易或高风险，不自动升优先级。 |

## 接近到位

No near-zone symbols within the configured alert buffer.

## 结构好但未到位 / 不追高

No symbol is flagged as too extended.

## 5个交易日内已提醒

No duplicate signal suppressed.

## 指数 / 杠杆 / 对冲参考

| Ticker | Role | Close | Trend | Nearest MA Alert | Note |
|---|---|---:|---|---:|---|
| NDX(nasdaq) | market_filter | 29,234.99 | strong_uptrend | MA10 26,254.14 | 市场温度计；个股A级信号最好发生在NDX强趋势或回踩企稳时。 |

## 回避 / 数据不足 / 备用源

No data issue.

Soft data notes kept in radar:
- NATKY(nasdaq): fallback_after:futu: Futu returned no data for US.NATKY: US OTC market quote is not available for NATKY.
- NNOMF(nasdaq): fallback_after:futu: Futu returned no data for US.NNOMF: Unknown stock. NNOMF
- NDX(nasdaq): fallback_after:futu: Futu returned no data for US.NDX: Unknown stock. NDX

## Full Radar Snapshot

| Ticker | Grade | Trend | Close | Next MA Alert | Cross Age | Themes |
|---|---|---|---:|---:|---|---|
| NATKY(nasdaq) | A | strong_uptrend | 80.00 | MA20 77.73 | 5>10:3w | uranium/Kazakhstan/nuclear |
| NNOMF(nasdaq) | C | weak | 0.693 | MA10 0.692 | 5>10:2w | battery materials/Canada |
| NDX(nasdaq) | CONTEXT | strong_uptrend | 29,234.99 | MA10 26,254.14 | 5>10:2w, 10>20:0w | market regime/index |
