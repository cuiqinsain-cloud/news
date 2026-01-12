#!/usr/bin/env python3
import sys
import re
import json
from datetime import datetime
from urllib.request import Request, urlopen
import os


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari"


def fetch_text(url: str, referer: str = None, encoding: str = "utf-8") -> str:
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    # Optional anti-scraping token header used by 10jqka; if provided, include it
    hx = os.environ.get("HEXIN_V")
    if hx:
        headers["hexin-v"] = hx
    req = Request(url, headers=headers)
    with urlopen(req, timeout=20) as resp:
        data = resp.read()
    try:
        return data.decode(encoding, errors="ignore")
    except Exception:
        return data.decode("utf-8", errors="ignore")


def parse_ashare_news_and_reports(html: str):
    news_items = []
    report_items = []

    # 热点新闻块：dl 项，包含日期和摘要
    # Pattern for primary highlighted dl entries (with [YYYY-MM-DD])
    for m in re.finditer(
        r"<dl>\s*<dt>\s*<a[^>]+href=\"(?P<href>[^\"]+)\"[^>]*title=\"(?P<title>[^\"]+)\"[\s\S]*?<span[^>]*class=\"fr date\"[^>]*>\[(?P<date>\d{4}-\d{2}-\d{2})\]</span>",
        html,
    ):
        news_items.append({
            "title": m.group("title"),
            "url": m.group("href"),
            "date": m.group("date"),
        })

    # 次级列表：ul.news_lists li a，日期为 MM/DD，年可从链接路径推断
    for m in re.finditer(
        r"<li>\s*<a[^>]+href=\"(?P<href>http://news\.10jqka\.com\.cn/field/\d{8}/[\w]+\.shtml)\"[^>]*>\s*<span>(?P<md>\d{2}/\d{2})</span>\s*(?P<title>[^<]+)</a>",
        html,
    ):
        href = m.group("href")
        title = m.group("title").strip()
        md = m.group("md")
        # Extract YYYYMMDD from href
        ymd_match = re.search(r"/field/(\d{8})/", href)
        if ymd_match:
            ymd = ymd_match.group(1)
            date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
        else:
            # Fallback: use current year (less precise)
            date = f"{datetime.now().year}-{md.replace('/', '-') }"
        news_items.append({"title": title, "url": href, "date": date})

    # 相关研报：dl 块，class 客户端链接到 field/sr/，有 <span class="date">YYYY-MM-DD</span>
    for m in re.finditer(
        r"<dl>\s*<dt>[\s\S]*?<a[^>]+href=\"(?P<href>http://news\.10jqka\.com\.cn/field/sr/\d{8}/[\w]+\.shtml[^\"]*)\"[^>]*title=\"(?P<title>[^\"]+)\"[\s\S]*?<span[^>]*class=\"date\"[^>]*>(?P<date>\d{4}-\d{2}-\d{2})</span>",
        html,
    ):
        report_items.append({
            "title": m.group("title"),
            "url": m.group("href"),
            "date": m.group("date"),
        })

    return news_items, report_items


def fetch_hk_news_json(code: str, page: int = 1, limit: int = 50):
    url = f"https://basic.10jqka.com.cn/basicapi/notice/news?type=hk&code={code}&current={page}&limit={limit}"
    txt = fetch_text(url, referer=f"https://basic.10jqka.com.cn/176/{code}/news.html")
    try:
        obj = json.loads(txt)
    except Exception:
        return []
    data = (obj.get("data") or {}).get("data") or []
    items = []
    for it in data:
        items.append({
            "title": it.get("title") or "",
            "url": it.get("client_url") or it.get("pc_url") or it.get("mobile_url") or "",
            "date": it.get("date") or "",
            "source": it.get("source") or "",
        })
    return items


def in_range(date_str: str, start: str, end: str) -> bool:
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        s = datetime.strptime(start, "%Y-%m-%d")
        e = datetime.strptime(end, "%Y-%m-%d")
        return s <= d <= e
    except Exception:
        return True


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 scripts/fetch_10jqka_stock_news.py <code> <start_date> <end_date>")
        print("Example: python3 scripts/fetch_10jqka_stock_news.py 688111 2025-12-01 2026-01-12")
        print("         python3 scripts/fetch_10jqka_stock_news.py HK2097 2026-01-01 2026-01-12")
        sys.exit(1)
    code = sys.argv[1].strip()
    start = sys.argv[2].strip()
    end = sys.argv[3].strip()

    out = {"code": code, "start": start, "end": end, "hot_news": [], "related_reports": []}

    if code.upper().startswith("HK"):
        # 港股：使用 JSON 接口
        news_items = fetch_hk_news_json(code, page=1, limit=100)
        out["hot_news"] = [it for it in news_items if it.get("date") and in_range(it["date"], start, end)]
        # 相关研报：暂未找到公开 JSON 接口，留空或后续扩展
        out["related_reports"] = []
    else:
        # A股：使用 HTML 片段接口
        url = f"https://stockpage.10jqka.com.cn/ajax/code/{code}/type/news/"
        html = fetch_text(url, referer=f"https://stockpage.10jqka.com.cn/{code}/news/", encoding="gbk")
        news_items, report_items = parse_ashare_news_and_reports(html)
        out["hot_news"] = [it for it in news_items if it.get("date") and in_range(it["date"], start, end)]
        out["related_reports"] = [it for it in report_items if it.get("date") and in_range(it["date"], start, end)]

    # 输出为 JSON，便于后续处理
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
