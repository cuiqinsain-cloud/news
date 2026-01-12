#!/usr/bin/env python3
import json
import sys
import time
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
DEFAULT_PARAMS = {
    "client": "web",
    "biz": "web_news_col",
    # column set per request: 350 国内经济, 351 国际经济
    "order": 1,
    "needInteractData": 0,
    "page_size": 50,  # larger page size to reduce requests
    "fields": "code,showTime,title,mediaName,summary,image,url,uniqueUrl,Np_dst",
    "types": "1,20",
}


def fetch_page(page_index: int, column: int):
    params = DEFAULT_PARAMS.copy()
    params["page_index"] = page_index
    params["column"] = column
    params["req_trace"] = int(time.time() * 1000)
    url = API_BASE + "?" + urlencode(params)
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
        # Use a generic referer; endpoint works for both columns
        "Referer": "https://finance.eastmoney.com/a/",
    })
    with urlopen(req, timeout=20) as resp:
        data = resp.read()
    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception:
        # Some endpoints may return JSONP; try to strip callback
        text = data.decode("utf-8", errors="ignore")
        start = text.find("({")
        end = text.rfind("})")
        if start != -1 and end != -1:
            obj = json.loads(text[start + 1:end + 1])
        else:
            raise
    if str(obj.get("code")) not in ("1", 1):
        raise RuntimeError(f"API error: {obj.get('message')} ({obj.get('code')})")
    return obj.get("data", {})


def get_today_news(column: int):
    """Back-compat: fetch only today's news for a column."""
    today = datetime.now().strftime("%Y-%m-%d")
    return get_news_by_date_range(column, today, today)


def get_news_by_date_range(column: int, start_date: str, end_date: str):
    """Fetch news for a column within [start_date, end_date] inclusive (YYYY-MM-DD).

    Pagination strategy: keep fetching until we encounter a page where all items
    are strictly below `start_date` (older than the requested window). This avoids
    prematurely stopping on pages that are above the range (e.g., today's items
    when fetching yesterday).
    """
    results = []
    page_index = 1
    below_start_pages = 0
    while True:
        data = fetch_page(page_index, column)
        items = data.get("list") or []
        if not items:
            break
        any_in_range = False
        all_below_start = True
        for it in items:
            show_time_full = it.get("showTime") or ""
            show_date = (show_time_full.split(" ")[0] or "").strip()
            if start_date <= show_date <= end_date:
                any_in_range = True
                results.append({
                    "title": it.get("title") or "",
                    "summary": it.get("summary") or "",
                    "url": it.get("url") or it.get("uniqueUrl") or "",
                    "showTime": show_time_full,
                })
            # If any item is not strictly below the start date, we cannot stop yet
            if show_date >= start_date:
                all_below_start = False

        # Track pages that are entirely below the start date
        if all_below_start:
            below_start_pages += 1
        else:
            below_start_pages = 0

        # If we've reached content entirely older than the requested window, we can stop
        if below_start_pages >= 1:
            break

        page_index += 1
        if page_index > 100:  # safety cap
            break
    return results


def build_html(items):
    dt = datetime.now().strftime("%Y-%m-%d")
    head = (
        "<!DOCTYPE html>\n"
        "<html lang=\"zh-CN\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\" />\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
        "  <title>国内经济 - 今日新闻（" + dt + "）</title>\n"
        "  <style>\n"
        "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif; margin: 20px; }\n"
        "    h1 { font-size: 20px; margin-bottom: 12px; }\n"
        "    .item { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 10px; }\n"
        "    .title { cursor: pointer; color: #0366d6; font-weight: 600; display: inline-block; }\n"
        "    .meta { color: #6b7280; font-size: 12px; margin-left: 8px; }\n"
        "    .summary { display: none; margin-top: 8px; line-height: 1.6; }\n"
        "    .link { display: inline-block; margin-top: 8px; margin-right: 10px; font-size: 12px; color: #374151; }\n"
        "    .comment strong { color: #111827; }\n"
        "  </style>\n"
        "  <script>\n"
        "    function toggle(id) {\n"
        "      var el = document.getElementById(id);\n"
        "      if (!el) return;\n"
        "      el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';\n"
        "    }\n"
        "  </script>\n"
        "</head>\n"
        "<body>\n"
        "  <h1>东方财富 · 国内经济 今日新闻（" + dt + "）</h1>\n"
    )
    parts = [head]
    if not items:
        parts.append("<p>未获取到今日新闻。</p>")
    for idx, it in enumerate(items, start=1):
        sid = f"summary-{idx}"
        title = (it["title"] or "").replace("<", "&lt;").replace(">", "&gt;")
        summary = (it["summary"] or "").replace("<", "&lt;").replace(">", "&gt;")
        url = it["url"] or ""
        time_str = it.get("showTime") or ""
        parts.append(
            f"""
  <div class=\"item\">
    <a class=\"title\" onclick=\"toggle('{sid}')\">{title}</a>
    <span class=\"meta\">{time_str}</span>
    <div id=\"{sid}\" class=\"summary\">{summary}</div>
    <a class=\"link\" href=\"{url}\" target=\"_blank\">原文链接</a>
  </div>
"""
        )
    parts.append("</body>\n</html>")
    return "".join(parts)


def build_html_tabs(domestic_items, international_items, industry_reports):
    dt = datetime.now().strftime("%Y-%m-%d")
    head = (
        "<!DOCTYPE html>\n"
        "<html lang=\"zh-CN\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\" />\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
        "  <title>今日新闻（" + dt + "）</title>\n"
        "  <style>\n"
        "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif; margin: 20px; }\n"
        "    h1 { font-size: 20px; margin-bottom: 12px; }\n"
        "    .tabs { margin-bottom: 12px; }\n"
        "    .tab-btn { display: inline-block; padding: 6px 10px; margin-right: 8px; border: 1px solid #e5e7eb; border-radius: 6px; cursor: pointer; background: #f9fafb; }\n"
        "    .tab-btn.active { background: #e5e7eb; }\n"
        "    .item { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 10px; }\n"
        "    .title { cursor: pointer; color: #0366d6; font-weight: 600; display: inline-block; }\n"
        "    .meta { color: #6b7280; font-size: 12px; margin-left: 8px; }\n"
        "    .summary { display: none; margin-top: 8px; line-height: 1.6; }\n"
        "    .link { display: block; margin-top: 8px; font-size: 12px; color: #374151; }\n"
        "  </style>\n"
        "  <script>\n"
        "    function toggle(id) {\n"
        "      var el = document.getElementById(id);\n"
        "      if (!el) return;\n"
        "      el.style.display = (el.style.display === 'none' || el.style.display === '') ? 'block' : 'none';\n"
        "    }\n"
        "    function switchTab(tab){\n"
        "      var dom = document.getElementById('domestic');\n"
        "      var intl = document.getElementById('international');\n"
        "      var ind = document.getElementById('industry');\n"
        "      var b1 = document.getElementById('btn-domestic');\n"
        "      var b2 = document.getElementById('btn-international');\n"
        "      var b3 = document.getElementById('btn-industry');\n"
        "      if(tab==='domestic'){\n"
        "        dom.style.display='block'; intl.style.display='none'; ind.style.display='none';\n"
        "        b1.classList.add('active'); b2.classList.remove('active'); b3.classList.remove('active');\n"
        "      } else if(tab==='international'){\n"
        "        dom.style.display='none'; intl.style.display='block'; ind.style.display='none';\n"
        "        b1.classList.remove('active'); b2.classList.add('active'); b3.classList.remove('active');\n"
        "      } else {\n"
        "        dom.style.display='none'; intl.style.display='none'; ind.style.display='block';\n"
        "        b1.classList.remove('active'); b2.classList.remove('active'); b3.classList.add('active');\n"
        "      }\n"
        "    }\n"
        "    window.addEventListener('DOMContentLoaded', function(){ switchTab('domestic'); });\n"
        "  </script>\n"
        "</head>\n"
        "<body>\n"
        "  <h1>东方财富 · 今日新闻（" + dt + "）</h1>\n"
        "  <div class=\"tabs\">\n"
        "    <button id=\"btn-domestic\" class=\"tab-btn\" onclick=\"switchTab('domestic')\">国内经济</button>\n"
        "    <button id=\"btn-international\" class=\"tab-btn\" onclick=\"switchTab('international')\">国际经济</button>\n"
        "    <button id=\"btn-industry\" class=\"tab-btn\" onclick=\"switchTab('industry')\">行业研报</button>\n"
        "  </div>\n"
    )
    parts = [head]


    def render_section(items, section_id):
        out = []
        out.append(f"<div id=\"{section_id}\" style=\"display:none\">\n")
        if not items:
            out.append("<p>未获取到今日新闻。</p>\n")
        for idx, it in enumerate(items, start=1):
            sid = f"{section_id}-summary-{idx}"
            cid = f"{section_id}-comment-{idx}"
            title = (it.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")
            summary = (it.get("summary") or "").replace("<", "&lt;").replace(">", "&gt;")
            url = it.get("url") or ""
            time_str = it.get("showTime") or ""
            out.append(
                f"""
  <div class=\"item\">\n
    <a class=\"title\" onclick=\"toggle('{sid}')\">{title}</a>
    <span class=\"meta\">{time_str}</span>
    <div id=\"{sid}\" class=\"summary\">{summary}</div>
    <a class=\"link\" href=\"{url}\" target=\"_blank\">原文链接</a>
  </div>
"""
            )
        out.append("</div>\n")
        return "".join(out)

    parts.append(render_section(domestic_items, "domestic"))
    parts.append(render_section(international_items, "international"))
    # 行业研报：仅显示行业名称和报告标题（报告标题可点击）
    parts.append("<div id=\"industry\" style=\"display:none\">\n")
    if not industry_reports:
        parts.append("<p>未获取到行业研报。</p>\n")
    else:
        for idx, ir in enumerate(industry_reports, start=1):
            ind = (ir.get("industryName") or "").replace("<", "&lt;").replace(">", "&gt;")
            title = (ir.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")
            url = ir.get("link") or ""
            # 仅显示日期部分，去除时间戳
            time_str = (ir.get("publishDate") or "")[:10]
            parts.append(
                f"""
  <div class=\"item\">\n
    <div><span class=\"meta\">行业：</span>{ind}</div>
    <a class=\"title\" href=\"{url}\" target=\"_blank\">{title}</a>
    <span class=\"meta\">{time_str}</span>
  </div>
"""
            )
    parts.append("</div>\n")
    parts.append("</body>\n</html>")
    return "".join(parts)


def build_comment_html(title: str, summary: str, cid: str) -> str:
    """生成基于标题/摘要的四维度简评。"""
    t = (title or "")
    s = (summary or "")

    def has_any(text, kws):
        return any(k in text for k in kws)

    if has_any(t+s, ["国务院", "中央", "发改委", "财政部", "央行", "监管", "政策", "措施", "指导", "推进"]):
        political = "政策导向与监管节奏值得关注，需跟踪配套细则与执行力度。"
    else:
        political = "对政策层面的直接影响有限，关注地方落实与舆情反馈。"

    if has_any(t+s, ["GDP", "通胀", "物价", "就业", "消费", "投资", "出口", "外贸", "融资", "货币", "利率", "流动性"]):
        economic = "对宏观变量（消费/投资/外贸或流动性）可能产生边际影响，需结合数据验证。"
    else:
        economic = "宏观层面影响偏中性，以结构性变化为主。"

    if has_any(t+s, ["航空", "新能源", "电力", "半导体", "地产", "汽车", "医药", "互联网", "券商", "银行", "AI", "机器人"]):
        industry = "对相关产业链景气度与竞争格局有潜在影响，关注上下游传导。"
    else:
        industry = "行业影响以情绪与预期为主，实质变化需观察订单与价格信号。"

    if has_any(t+s, ["公司", "企业", "龙头", "上市", "并购", "投资", "产能", "签约", "订单", "项目", "落地"]):
        enterprise = "龙头与具备技术/渠道/成本优势的企业或更受益，关注执行与现金流质量。"
    else:
        enterprise = "对企业经营的直接影响不强，更多体现在预期与估值层面。"

    return f"""
    <div id=\"{cid}\" class=\"comment\">
      <div><strong>政治：</strong>{political}</div>
      <div><strong>经济：</strong>{economic}</div>
      <div><strong>行业：</strong>{industry}</div>
      <div><strong>企业发展：</strong>{enterprise}</div>
    </div>
    """


def load_filter_config(path: str):
    # Filtering removed; keep stub for backward compatibility.
    return None


def filter_items(items, cfg):
    # Filtering removed per user request
    return items

def fetch_industry_reports(limit: int = 50, begin: str = None, end: str = None):
    import json as _json
    from urllib.parse import urlencode as _urlencode
    from datetime import datetime as _dt

    base = "https://reportapi.eastmoney.com/report/list"
    today = _dt.now().strftime("%Y-%m-%d")
    if not begin and not end:
        begin = end = today
    elif begin and not end:
        end = begin
    params = {
        "cb": "cb",
        "industryCode": "*",
        "pageSize": max(limit, 50),
        "industry": "*",
        "rating": "*",
        "ratingChange": "*",
        # 指定时间范围（默认今天）
        "beginTime": begin,
        "endTime": end,
        "pageNo": 1,
        "fields": "",
        "qType": 1,  # 行业研报
    }
    url = base + "?" + _urlencode(params)
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://data.eastmoney.com/report/industry.jshtml",
    })
    with urlopen(req, timeout=20) as resp:
        txt = resp.read().decode("utf-8", errors="ignore")
    # JSONP: cb({...})
    start_idx = txt.find("(")
    end_idx = txt.rfind(")")
    if start_idx == -1 or end_idx == -1:
        return []
    obj = _json.loads(txt[start_idx + 1:end_idx])
    data = obj.get("data") or []
    # 按日期严格过滤（防止接口边界差异）
    b, e = begin, end
    def _date10(v):
        try:
            return str(v)[:10]
        except Exception:
            return ""
    today_list = [
        it for it in data
        if b <= _date10(it.get("publishDate")) <= e
    ]
    out = []
    for it in today_list[:limit]:
        title = it.get("title") or ""
        industry_name = it.get("industryName") or it.get("indvInduName") or ""
        info_code = it.get("infoCode") or ""
        publish_date = it.get("publishDate") or ""
        link = f"https://data.eastmoney.com/report/zw_industry.jshtml?infocode={info_code}"
        out.append({
            "title": title,
            "industryName": industry_name,
            "link": link,
            "publishDate": publish_date,
        })
    return out

def main(out_path: str, config_path=None, start_date: str = None, end_date: str = None):
    # 国内经济 column 350, 国际经济 column 351
    if start_date and end_date:
        domestic = filter_items(get_news_by_date_range(350, start_date, end_date), None)
        international = filter_items(get_news_by_date_range(351, start_date, end_date), None)
        industry_reports = fetch_industry_reports(begin=start_date, end=end_date)
    else:
        domestic = filter_items(get_today_news(350), None)
        international = filter_items(get_today_news(351), None)
        industry_reports = fetch_industry_reports()
    html = build_html_tabs(domestic, international, industry_reports)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {len(domestic)} domestic + {len(international)} international + {len(industry_reports)} industry reports to {out_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "eastmoney_gn_gj_today.html"
    # 可选日期范围参数：YYYY-MM-DD YYYY-MM-DD
    if len(sys.argv) >= 4:
        s, e = sys.argv[2], sys.argv[3]
        main(out, start_date=s, end_date=e)
    else:
        main(out)
