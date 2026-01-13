# News Assistant README

This document summarizes the available news sources, features, and how to interact with me to fetch and compose news pages.

## Capabilities
- Eastmoney Domestic/International News
  - Source: `https://np-listapi.eastmoney.com/comm/web/getNewsByColumns`
  - Columns: `350` (Domestic), `351` (International)
  - Date range: supported (`YYYY-MM-DD` start/end)
- Eastmoney Industry Reports
  - Source: `https://reportapi.eastmoney.com/report/list` (industry reports `qType=1`)
  - Date range: supported (`beginTime`/`endTime`)
  - Display shows only the date part (no timestamp)
- 10jqka Stock Page (optional per request)
  - Pages: `https://stockpage.10jqka.com.cn/<code>/news/` (A-share like `688111`; HK needs prefix, e.g. `HK2097`)
  - A-share: parses HTML fragment for “热点新闻”“相关研报”
  - HK: JSON endpoint for “热点新闻” (`basicapi/notice/news`); related reports not exposed as JSON
  - Date range: supported via builder
- Combined HTML Builder
  - Single page with tabs: Domestic, International, Industry; optional per‑stock sections with sub‑tabs (Hot News, Related Reports)
  - Stock sections appear only if you specify `--codes`

## How To Interact
- Tell me a date or date range (`YYYY-MM-DD`), and optionally a list of stock codes.
- I will always build and open a combined HTML page with the requested sections.
- If you don’t specify stock codes, the page will include only the default sections（国内经济、国际经济、行业研报）.
- 即使以“给我数据/JSON”等方式描述需求，最终我也会生成并打开 HTML 页面；如需 JSON，仅用于内部抓取调试，不再作为默认输出。

## Common Commands
Note: output HTML filenames now auto-append a timestamp suffix like `_YYYYMMDD_HHMMSS`. Pass `--no-ts` to keep the exact filename.
- Today (no stocks):
  - `python3 scripts/build_combined_news.py combined_today.html --start $(date +%F) --end $(date +%F)`
  - Open latest: `open $(ls -t Data/combined_today_*.html | head -1)`
- Yesterday (no stocks):
  - `python3 scripts/build_combined_news.py combined_yesterday.html --start $(date -v-1d +%F) --end $(date -v-1d +%F)`
  - Open latest: `open $(ls -t Data/combined_yesterday_*.html | head -1)`
- Specific range (no stocks):
  - `python3 scripts/build_combined_news.py combined_range.html --start 2025-12-01 --end 2026-01-12`
  - Open latest: `open $(ls -t Data/combined_range_*.html | head -1)`
- Include stocks (A/HK mixed):
  - `python3 scripts/build_combined_news.py combined.html --codes 688111,HK2097 --start 2025-12-01 --end 2026-01-12`
  - Open latest: `open $(ls -t Data/combined_*.html | head -1)`
  - Per-stock range (uniform): add `--stock-start 2026-01-01 --stock-end 2026-01-12`
  - Per-code override: repeat `--code-range`, e.g. `--code-range 688111:2026-01-10:2026-01-12 --code-range HK2097:2026-01-08:2026-01-12`
- A-share stock JSON:
  - `python3 scripts/fetch_10jqka_stock_news.py 688111 2025-12-01 2026-01-12`
- HK stock JSON:
  - `python3 scripts/fetch_10jqka_stock_news.py HK2097 2025-12-01 2026-01-12`

## Inputs You Provide
- Date or date range: `YYYY-MM-DD` (start and end)
- Optional stock codes:
  - A-share: numeric (e.g., `688111`)
  - HK: prefixed with `HK` (e.g., `HK2097`)

## Outputs You Get
- Combined HTML page with tabs（默认包含：国内经济、国际经济、行业研报；可选：个股标签）
- 不再单独返回 JSON 作为最终结果；个股 JSON 抓取仅用于内部流程以生成页面。

## Notes & Caveats
- Anti-scraping: HK JSON may require a `hexin-v` header. If needed, set an environment variable before running:
  - `export HEXIN_V="<value from browser requests>"`
- Industry report timestamps are trimmed to date only.
- Filtering is minimal by design; pages show items within the requested date range.
 - Disable timestamp suffix: add `--no-ts` to keep the exact output filename.

## Examples of Asking
- “我要看今天的新闻”
  - 我会构建当天的综合 HTML 页面（默认三大板块），并打开。
- “我要看昨天的新闻，并加入 688111 和 HK2097”
  - 我会构建昨天的综合 HTML 页面，包含所列个股标签，并打开。
- “给我 688111 的热点新闻和相关研报，时间 2025-12-01 到 2026-01-12”
  - 我会抓取对应数据并直接生成 HTML 页面展示（不再单独返回 JSON）。

## Files & Scripts
- `scripts/fetch_eastmoney_cgnjj.py`: Eastmoney domestic/international news + industry reports (supports date ranges)
- `scripts/fetch_10jqka_stock_news.py`: 10jqka per‑stock Hot News/Related Reports (A/HK)
- `scripts/build_combined_news.py`: Compose combined HTML with optional per‑stock tabs
- `source.md`: Source details and usage
