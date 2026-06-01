# 美股/ADR 周线回踩监控

这是一个轻量本地监控器，优先用本机 `FutuOpenD` 拉取日线数据，再重采样为周线；如果美股/ADR/ETF 从 Futu 取不到，会自动退回 Nasdaq 公开日线接口。

核心逻辑只使用 Python 标准库，不需要安装 `pandas`、`yfinance` 或其他包。Futu 数据源需要额外安装 `futu-api`。

如果 OpenD 未启动或某个美股标的 Futu 取不到，脚本会自动走 Nasdaq 兜底，尽量减少硬性 data error。港股/A股这类非美股代码不会乱走 Nasdaq；新 ETF 或历史很短的标的会保留在报告里，并标注 `short_history`。

## 快速使用

在本目录运行：

```bash
python3 monitor.py
```

默认会读取 `watchlist.yml`，输出：

- `reports/latest.md`：给人看的 Markdown 报告
- `reports/latest.json`：结构化结果
- `reports/state.json`：5 个交易日去重状态

只看几个标的：

```bash
python3 monitor.py --symbols GOOG AGRO RKLB BABA
```

想忽略去重、把当前所有命中都显示出来：

```bash
python3 monitor.py --no-dedupe
```

强制只用 Futu：

```bash
python3 monitor.py --provider futu
```

默认 `auto` 数据源会先试 Futu，再试 Nasdaq：

```bash
python3 monitor.py --provider auto
```

使用旧入口也可以：

```bash
python3 weekly_pullback_monitor.py
```

## 信号含义

- `单纯回踩 MAxx`：周线低点或收盘进入 MA10/20/30/60/120 附近的动态缓冲区。
- `交叉后上沿加仓区`：MA5/10/20/30/60 近期出现多头交叉，价格回到短中期均线簇上沿附近，类似你圈出的 `GOOG`、`AGRO`。
- `今日到位`：本次真正触发提醒的标的。
- `接近到位`：离下一条提醒均线不远，可以提前放进人工观察。
- `结构好但未到位 / 不追高`：趋势和叙事可能不错，但离均线太远，原则是等回踩。
- `指数 / 杠杆 / 对冲参考`：`.NDX`、`AAOX`、`SNDQ` 这类不参与普通个股加仓评分，只做市场温度或风险提示。

## 配置

`watchlist.yml` 是 JSON-compatible YAML。这样做是为了保持零依赖：Python 标准库可以直接读取它，同时文件扩展名保留为计划里的 `.yml`。

每个标的可配置：

- `symbol`：提醒里显示的 ticker
- `source_symbol`：可选，Nasdaq 备用源查询用 ticker
- `assetclass`：默认 `stocks`，也可用 `etf`、`index`
- `themes`：叙事标签
- `risk`：`low`、`medium`、`medium_high`、`high`、`very_high`、`hedge`
- `narrative_score` / `quality_score`：1-5 分
- `watch_mas`：要监控的周线均线周期
- `exclude_from_stock_radar`：设为 `true` 时只做参考，不参与普通个股评分
- `futu_code`：可选，Futu 行情代码，例如 `US.SNDQ`、`US.GOOG`、`HK.09888`
- `futu_market`：可选，默认 `US`；港股可设 `HK`，A股可设 `SH` 或 `SZ`
- `nasdaq_fallback`：可选，设为 `false` 时即使是美股也不走 Nasdaq 备用源

## Futu 数据源

Futu OpenAPI 不是把 API key 直接写进 HTTP 请求的模式。推荐方式是：

1. 在本机启动并登录 `FutuOpenD`。
2. 安装可选依赖：

```bash
python3 -m pip install -r requirements-futu.txt
```

3. 如果 OpenD 不在默认地址，设置环境变量：

```bash
export FUTU_OPEND_HOST=127.0.0.1
export FUTU_OPEND_PORT=11111
```

4. 运行：

```bash
python3 monitor.py --provider auto
```

如果你只想测试 Futu，不走 Nasdaq：

```bash
python3 monitor.py --provider futu --symbols SNDQ
```

不要把富途账号、解锁密码、RSA 私钥或任何 API 凭证写进 `watchlist.yml`，也不要发到聊天里。需要加密连接时，在你的本机 OpenD/Python 环境配置。

## 自动提醒

推荐节奏是香港时间周二到周六早上 06:15 跑一次，对应美股上一个交易日收盘后。

自动化任务会执行本目录的 `python3 monitor.py`，然后把报告里的 `今日到位`、`接近到位` 和 `结构好但未到位` 回到 Codex 线程。遇到美股假期或同一信号 5 个交易日内重复出现时，会被 `reports/state.json` 去重压住。

## 数据提示

报告里的 `fallback_after` 和 `short_history` 都是软提示：

- `fallback_after`：Futu 取不到该美股/ADR/OTC，已自动用 Nasdaq 备用源。
- `short_history`：历史数据太短，仍保留在雷达里，但均线结论要打折。

真正所有来源都取不到时，才会进入硬性 data issue。

## 注意

这套工具是研究和提醒辅助，不是自动交易系统，也不是买卖建议。高波动、小盘、杠杆和反向产品默认会被降级或隔离。
