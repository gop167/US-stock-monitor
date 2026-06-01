# 美股/ADR 周线回踩监控

- Generated: 2026-05-29 08:28
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

No context-only symbol configured.

## 回避 / 数据不足 / 备用源

- GOOG: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- RKLB: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- AGRO: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- BABA: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- CRCL: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- INTC: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- MU: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- SNDK: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- AAOI: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- LITE: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- ASML: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- APP: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- FIG: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- TEM: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- DUOL: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- SAP: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- PDD: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- JD: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- LI: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- XPEV: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- NIO: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- MBGYY: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- COIN: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- BMNR: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- BTCS: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- SBET: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- ARBK: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- AIFC: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- VCX: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- ORBS: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- WINT: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- SUIG: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- CCJ: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- LEU: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- CEG: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- VST: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- OKLO: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- NATKY: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- LNG: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- FLNC: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- RACE: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- VWAGY: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- ESLOY: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- NNOMF: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- SNDQ: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- AAOX: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>
- NDX: futu: futu-api is not installed; run `python3 -m pip install futu-api` first; nasdaq: <urlopen error [Errno 8] nodename nor servname provided, or not known>

## Full Radar Snapshot

| Ticker | Grade | Trend | Close | Next MA Alert | Cross Age | Themes |
|---|---|---|---:|---:|---|---|
