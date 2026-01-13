# 新闻源一览

本项目当前使用的新闻与研报数据源，以及对应的脚本与使用方式。

输出目录：若未在输出路径中显式指定目录，生成的 HTML 默认写入 `Data/`（会自动创建）。

## 东方财富 · 新闻栏目（国内/国际）
- 接口：`https://np-listapi.eastmoney.com/comm/web/getNewsByColumns`
- 栏目参数：`column=350`（国内经济）、`column=351`（国际经济）
- 脚本：`scripts/fetch_eastmoney_cgnjj.py`
- 支持时间范围：`get_news_by_date_range(column, start, end)`；CLI 可传入 `YYYY-MM-DD YYYY-MM-DD`。
- 输出：生成含“国内/国际/行业研报”三栏可切换的页面，新闻标题可折叠摘要。

## 东方财富 · 行业研报
- 接口：`https://reportapi.eastmoney.com/report/list`（`qType=1` 行业研报）
- 支持时间范围：传入 `beginTime`/`endTime`（脚本参数支持 `YYYY-MM-DD YYYY-MM-DD`）。
- 展示：显示行业名称与报告标题（标题可点击跳转原文）。
- 脚本：`scripts/fetch_eastmoney_cgnjj.py`

## 同花顺 · 个股页面（热点新闻/相关研报）
- 页面示例：`https://stockpage.10jqka.com.cn/688111/news/`、`https://stockpage.10jqka.com.cn/HK2097/news/`
- A股热点新闻与相关研报：
  - 接口（HTML片段）：`https://stockpage.10jqka.com.cn/ajax/code/<A股代码>/type/news/`
  - 解析方式：从返回的 HTML 片段中抽取“热点新闻”和“相关研报”条目（含标题、日期、原文链接）。
- 港股热点新闻：
  - 接口（JSON）：`https://basic.10jqka.com.cn/basicapi/notice/news?type=hk&code=<港股代码>&current=1&limit=50`
  - 注意：港股相关研报未发现公开 JSON 接口；后续可补充解析方案或替代来源。
- 代码规则：A股直接使用数字代码（如 `688111`）；港股需使用前缀 `HK`（如 `HK2097`）。
- 脚本：`scripts/fetch_10jqka_stock_news.py`

## 使用方法
1. 生成页面（支持指定时间范围）：
   - 当天：`python3 scripts/fetch_eastmoney_cgnjj.py Data/eastmoney_gn_gj_today.html`
   - 指定范围：`python3 scripts/fetch_eastmoney_cgnjj.py Data/eastmoney_gn_gj_range.html 2025-12-01 2026-01-12`
2. 获取同花顺个股“热点新闻/相关研报”（按时间范围）：
   - `python3 scripts/fetch_10jqka_stock_news.py 688111 2025-12-01 2026-01-12`
   - `python3 scripts/fetch_10jqka_stock_news.py HK2097 2026-01-05 2026-01-12`
   - 输出：标准 JSON（字段：`code`、`start`、`end`、`hot_news[]`、`related_reports[]`）。
3. 构建综合页面（国内/国际/行业研报 + 个股热点新闻/相关研报）：
   - 不含个股：`python3 scripts/build_combined_news.py combined_today.html --start 2025-12-01 --end 2026-01-12`
   - 含个股（需显式指定）：`python3 scripts/build_combined_news.py combined_today.html --codes 688111,HK2097 --start 2025-12-01 --end 2026-01-12`
   - 个股统一时间范围：添加 `--stock-start 2026-01-01 --stock-end 2026-01-12`
   - 单独设置某个代码：重复添加 `--code-range CODE:YYYY-MM-DD:YYYY-MM-DD`，如 `--code-range 688111:2026-01-10:2026-01-12 --code-range HK2097:2026-01-08:2026-01-12`
   - 说明：综合页面输出文件名默认追加时间戳后缀（例如 `combined_today_YYYYMMDD_HHMMSS.html`），并写入 `Data/` 目录。
4. 打开页面查看：
   - 东方财富（当天/指定范围）：`open Data/eastmoney_gn_gj_today.html` 或 `open Data/eastmoney_gn_gj_range.html`
   - 综合页面（打开最新）：`open $(ls -t Data/combined_today_*.html | head -1)`

## 备注
- 日期格式：统一采用 `YYYY-MM-DD`。
- 国内/国际/行业研报均支持“特定日期或时间范围”获取。
- 新闻条目过滤已移除，默认展示当天全部新闻（国内+国际）。
- 暂无外部配置文件；可通过修改脚本参数扩展功能。
 - 访问同花顺接口可能受防爬策略影响；如港股返回为空，可设置环境变量 `HEXIN_V` 以附加 `hexin-v` 请求头提升成功率：
   - `export HEXIN_V="<从浏览器请求中抓到的hexin-v值>"`
 - 个股数据为可选：仅在综合页面命令中使用 `--codes` 时才会抓取并展示个股的“热点新闻/相关研报”。
 - 行业研报时间显示已优化：仅显示日期（去除时间戳）。
  - 关闭综合页面时间戳：在命令后加 `--no-ts` 可保持输出文件名与传入一致（仍默认写入 `Data/` 目录）。
- 交互说明与整体概览：参见 `readme.md`。

## 未来扩展（可选）
- 增加其他新闻源：如新华社/央视、证券时报、RSS 源等。
- 增加持久化与历史浏览：存储每日 HTML 或结构化数据以便回溯。
