#!/usr/bin/env python3
import sys
import os
import importlib.util
from datetime import datetime
from urllib.request import Request, urlopen


def _load_module(path: str):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def in_range(date_str: str, start: str, end: str) -> bool:
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        s = datetime.strptime(start, "%Y-%m-%d")
        e = datetime.strptime(end, "%Y-%m-%d")
        return s <= d <= e
    except Exception:
        return True


def _theme_css(theme: str) -> str:
    t = (theme or "classic").lower()
    if t == "neon":
        return (
            "body{background:#0b0f19;color:#d1d5db;font-family:Inter,Roboto,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,'Noto Sans','PingFang SC','Microsoft YaHei',sans-serif;margin:0;}\n"
            ".container{max-width:1080px;margin:24px auto;padding:24px;}\n"
            ".title{font-size:22px;margin:0 0 16px;background:linear-gradient(90deg,#00e5ff,#a855f7);-webkit-background-clip:text;background-clip:text;color:transparent;}\n"
            ".tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;}\n"
            ".tab-btn{padding:8px 12px;border:1px solid rgba(0,229,255,.35);border-radius:10px;cursor:pointer;background:rgba(2,8,23,.6);color:#9beaf9;box-shadow:0 0 8px rgba(0,229,255,.25) inset,0 0 6px rgba(168,85,247,.25);transition:all .2s;}\n"
            ".tab-btn.active{background:rgba(168,85,247,.15);color:#e5e7eb;border-color:rgba(168,85,247,.45);}\n"
            ".subtabs{display:flex;gap:6px;margin:8px 0 12px;}\n"
            ".sub-btn{padding:6px 10px;border:1px solid rgba(0,229,255,.3);border-radius:8px;cursor:pointer;background:rgba(2,8,23,.5);color:#93c5fd;transition:.2s;}\n"
            ".sub-btn.active{background:rgba(0,229,255,.12);color:#e5e7eb;border-color:rgba(0,229,255,.5);}\n"
            ".item{border:1px solid rgba(148,163,184,.25);border-radius:12px;padding:12px;margin:10px 0;background:linear-gradient(180deg,rgba(13,18,28,.65),rgba(13,18,28,.4));box-shadow:0 2px 8px rgba(0,0,0,.35);}\n"
            ".title-link{color:#7dd3fc;text-decoration:none;font-weight:600;}\n"
            ".meta{color:#94a3b8;font-size:12px;margin-left:8px;}\n"
            ".link{display:block;margin-top:6px;font-size:12px;color:#cbd5e1;}\n"
            ".grid-bg{position:fixed;inset:0;background-image:radial-gradient(transparent 0,transparent 1px,rgba(45,212,191,.05) 1px),radial-gradient(transparent 0,transparent 1px,rgba(168,85,247,.06) 1px);background-size:20px 20px,32px 32px;pointer-events:none;opacity:.6;}\n"
        )
    if t == "glass":
        return (
            "body{background:linear-gradient(135deg,#0b1020,#121a2e 50%,#0b1020);color:#e2e8f0;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue','PingFang SC','Microsoft YaHei',sans-serif;margin:0;}\n"
            ".container{max-width:1080px;margin:24px auto;padding:24px;}\n"
            ".title{font-size:22px;margin:0 0 16px;color:#e2e8f0;}\n"
            ".tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;}\n"
            ".tab-btn{padding:8px 12px;border:1px solid rgba(226,232,240,.2);border-radius:12px;cursor:pointer;background:rgba(255,255,255,.06);backdrop-filter:blur(8px);color:#e2e8f0;box-shadow:0 8px 24px rgba(0,0,0,.25) inset,0 2px 8px rgba(0,0,0,.35);}\n"
            ".tab-btn.active{background:rgba(147,197,253,.15);border-color:rgba(147,197,253,.35);}\n"
            ".subtabs{display:flex;gap:6px;margin:8px 0 12px;}\n"
            ".sub-btn{padding:6px 10px;border:1px solid rgba(226,232,240,.18);border-radius:10px;background:rgba(255,255,255,.05);cursor:pointer;color:#e2e8f0;}\n"
            ".sub-btn.active{background:rgba(226,232,240,.12);}\n"
            ".item{border:1px solid rgba(226,232,240,.18);border-radius:14px;padding:14px;margin:10px 0;background:rgba(255,255,255,.06);backdrop-filter:blur(6px);}\n"
            ".title-link{color:#93c5fd;text-decoration:none;font-weight:600;}\n"
            ".meta{color:#cbd5e1;font-size:12px;margin-left:8px;}\n"
            ".link{display:block;margin-top:6px;font-size:12px;color:#e2e8f0;}\n"
        )
    if t == "terminal":
        return (
            "body{background:#0a0f0a;color:#c6f6d5;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,'Liberation Mono','Courier New',monospace;margin:0;}\n"
            ".container{max-width:1080px;margin:24px auto;padding:24px;}\n"
            ".title{font-size:22px;margin:0 0 16px;color:#68d391;}\n"
            ".tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;}\n"
            ".tab-btn{padding:8px 12px;border:1px solid #2f855a;border-radius:8px;cursor:pointer;background:#1a202c;color:#68d391;}\n"
            ".tab-btn.active{background:#22543d;color:#c6f6d5;}\n"
            ".subtabs{display:flex;gap:6px;margin:8px 0 12px;}\n"
            ".sub-btn{padding:6px 10px;border:1px solid #2f855a;border-radius:8px;cursor:pointer;background:#0f1418;color:#68d391;}\n"
            ".sub-btn.active{background:#22543d;color:#c6f6d5;}\n"
            ".item{border:1px solid #2f855a;border-radius:8px;padding:12px;margin:10px 0;background:#0f1410;box-shadow:0 2px 6px rgba(0,0,0,.4);}\n"
            ".title-link{color:#68d391;text-decoration:none;font-weight:700;}\n"
            ".meta{color:#9ae6b4;font-size:12px;margin-left:8px;}\n"
            ".link{display:block;margin-top:6px;font-size:12px;color:#c6f6d5;}\n"
        )
    # classic (existing styles)
    return (
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif; margin: 20px; }\n"
        "h1 { font-size: 20px; margin-bottom: 12px; }\n"
        ".tabs { margin-bottom: 12px; }\n"
        ".tab-btn { display: inline-block; padding: 6px 10px; margin-right: 8px; border: 1px solid #e5e7eb; border-radius: 6px; cursor: pointer; background: #f9fafb; }\n"
        ".tab-btn.active { background: #e5e7eb; }\n"
        ".item { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 10px; }\n"
        ".title-link { color: #0366d6; font-weight: 600; display: inline-block; text-decoration:none;}\n"
        ".meta { color: #6b7280; font-size: 12px; margin-left: 8px; }\n"
        ".link { display: block; margin-top: 8px; font-size: 12px; color: #374151; }\n"
        ".subtabs { margin-bottom: 8px; }\n"
        ".sub-btn { display: inline-block; padding: 4px 8px; margin-right: 6px; border: 1px solid #e5e7eb; border-radius: 6px; cursor: pointer; background: #fff; }\n"
        ".sub-btn.active { background: #e5e7eb; }\n"
    )

def build_html_combined(domestic_items, international_items, industry_reports, stock_sections, theme: str = "classic", page_title: str = None):
    dt = datetime.now().strftime("%Y-%m-%d")
    title_text = page_title or f"综合页面 · 新闻（{dt}）"
    head = (
        "<!DOCTYPE html>\n"
        "<html lang=\"zh-CN\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\" />\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n"
        "  <title>" + title_text + "</title>\n"
        "  <style>\n"
        + _theme_css(theme)
        + "  </style>\n"
        "  <script>\n"
        "    function switchTab(tab){\n"
        "      var ids = [""\n"
    )
    # list of tab ids
    tab_ids = ["domestic", "international", "industry"] + [f"stock-{code}" for code in stock_sections.keys()]
    head += ",".join([f"'tab-{tid}'" for tid in tab_ids]) + "]";
    head += (
        ";\n"
        "      for (var i=0;i<ids.length;i++){\n"
        "        var el = document.getElementById(ids[i]);\n"
        "        var btn = document.getElementById('btn-'+ids[i]);\n"
        "        if (ids[i] === 'tab-'+tab){ el.style.display='block'; if(btn) btn.classList.add('active'); } else { el.style.display='none'; if(btn) btn.classList.remove('active'); }\n"
        "      }\n"
        "    }\n"
        "    function switchStockTab(code, sub){\n"
        "      var hot = document.getElementById('stock-'+code+'-hot');\n"
        "      var rep = document.getElementById('stock-'+code+'-report');\n"
        "      var bhot = document.getElementById('btn-stock-'+code+'-hot');\n"
        "      var brep = document.getElementById('btn-stock-'+code+'-report');\n"
        "      if (sub==='hot'){ hot.style.display='block'; rep.style.display='none'; bhot.classList.add('active'); brep.classList.remove('active'); }\n"
        "      else { hot.style.display='none'; rep.style.display='block'; bhot.classList.remove('active'); brep.classList.add('active'); }\n"
        "    }\n"
        "    window.addEventListener('DOMContentLoaded', function(){ switchTab('domestic'); });\n"
        "  </script>\n"
        "</head>\n"
        "<body>\n"
        "  <div class=\"grid-bg\"></div>\n"
        "  <div class=\"container\">\n"
        "  <h1 class=\"title\">" + title_text + "</h1>\n"
        "  <div class=\"tabs\">\n"
        f"    <button id=\"btn-tab-domestic\" class=\"tab-btn\" onclick=\"switchTab('domestic')\">国内经济</button>\n"
        f"    <button id=\"btn-tab-international\" class=\"tab-btn\" onclick=\"switchTab('international')\">国际经济</button>\n"
        f"    <button id=\"btn-tab-industry\" class=\"tab-btn\" onclick=\"switchTab('industry')\">行业研报</button>\n"
    )
    # stock code buttons
    for code in stock_sections.keys():
        head += f"    <button id=\"btn-tab-stock-{code}\" class=\"tab-btn\" onclick=\"switchTab('stock-{code}')\">{code}</button>\n"
    head += "  </div>\n"

    parts = [head]

    def render_news_section(items, section_id, title_label):
        out = []
        out.append(f"<div id=\"tab-{section_id}\" style=\"display:none\">\n")
        out.append(f"<h2>{title_label}</h2>\n")
        if not items:
            out.append("<p>未获取到新闻。</p>\n")
        for it in items:
            t = (it.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")
            url = it.get("url") or ""
            time_str = (it.get("showTime") or it.get("date") or "")
            out.append(
                f"""
  <div class=\"item\">\n
    <a class=\"title-link\" href=\"{url}\" target=\"_blank\">{t}</a>
    <span class=\"meta\">{time_str}</span>
    <a class=\"link\" href=\"{url}\" target=\"_blank\">原文链接</a>
  </div>
"""
            )
        out.append("</div>\n")
        return "".join(out)

    # domestic/international
    parts.append(render_news_section(domestic_items, "domestic", "国内经济"))
    parts.append(render_news_section(international_items, "international", "国际经济"))

    # industry reports
    out = []
    out.append("<div id=\"tab-industry\" style=\"display:none\">\n")
    out.append("<h2>行业研报</h2>\n")
    if not industry_reports:
        out.append("<p>未获取到行业研报。</p>\n")
    else:
        for ir in industry_reports:
            ind = (ir.get("industryName") or "").replace("<", "&lt;").replace(">", "&gt;")
            title = (ir.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")
            url = ir.get("link") or ""
            time_str = ir.get("publishDate") or ""
            out.append(
                f"""
  <div class=\"item\">\n
    <div><span class=\"meta\">行业：</span>{ind}</div>
    <a class=\"title-link\" href=\"{url}\" target=\"_blank\">{title}</a>
    <span class=\"meta\">{time_str}</span>
  </div>
"""
            )
    out.append("</div>\n")
    parts.append("".join(out))

    # stock sections
    for code, sec in stock_sections.items():
        hot = sec.get("hot_news") or []
        rep = sec.get("related_reports") or []
        rs = (sec.get("range_start") or "").strip()
        re = (sec.get("range_end") or "").strip()
        if rs and re:
            if rs == re:
                range_label = f"（{rs}）"
            else:
                range_label = f"（{rs} 至 {re}）"
        else:
            range_label = ""
        parts.append(f"<div id=\"tab-stock-{code}\" style=\"display:none\">\n")
        parts.append(f"<h2 class=\"title\">个股 {code}{range_label}</h2>\n")
        parts.append(f"<div class=\"subtabs\">\n")
        parts.append(f"  <button id=\"btn-stock-{code}-hot\" class=\"sub-btn\" onclick=\"switchStockTab('{code}','hot')\">热点新闻</button>\n")
        parts.append(f"  <button id=\"btn-stock-{code}-report\" class=\"sub-btn\" onclick=\"switchStockTab('{code}','report')\">相关研报</button>\n")
        parts.append("</div>\n")
        # hot
        parts.append(f"<div id=\"stock-{code}-hot\" style=\"display:block\">\n")
        if not hot:
            parts.append("<p>暂无热点新闻。</p>\n")
        else:
            for it in hot:
                t = (it.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")
                url = it.get("url") or ""
                time_str = (it.get("date") or "")
                parts.append(
                    f"""
  <div class=\"item\">\n
    <a class=\"title-link\" href=\"{url}\" target=\"_blank\">{t}</a>
    <span class=\"meta\">{time_str}</span>
    <a class=\"link\" href=\"{url}\" target=\"_blank\">原文链接</a>
  </div>
"""
                )
        parts.append("</div>\n")
        # reports
        parts.append(f"<div id=\"stock-{code}-report\" style=\"display:none\">\n")
        if not rep:
            parts.append("<p>暂无相关研报。</p>\n")
        else:
            for it in rep:
                t = (it.get("title") or "").replace("<", "&lt;").replace(">", "&gt;")
                url = it.get("url") or ""
                time_str = (it.get("date") or "")
                parts.append(
                    f"""
  <div class=\"item\">\n
    <a class=\"title-link\" href=\"{url}\" target=\"_blank\">{t}</a>
    <span class=\"meta\">{time_str}</span>
    <a class=\"link\" href=\"{url}\" target=\"_blank\">原文链接</a>
  </div>
"""
                )
        parts.append("</div>\n")
        parts.append("</div>\n")

    parts.append("  </div>\n")
    parts.append("</body>\n</html>")
    return "".join(parts)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/build_combined_news.py <out.html> [--codes code1,code2] [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--stock-start YYYY-MM-DD] [--stock-end YYYY-MM-DD] [--code-range code:YYYY-MM-DD:YYYY-MM-DD] [--theme classic|neon|glass|terminal] [--no-ts]")
        print("Example: python3 scripts/build_combined_news.py combined_today.html --codes 688111,HK2097 --start 2025-12-01 --end 2026-01-12")
        sys.exit(1)
    out_path = sys.argv[1]
    codes = []
    start = datetime.now().strftime("%Y-%m-%d")
    end = start
    theme = "classic"
    append_ts = True
    stock_start = None
    stock_end = None
    code_ranges = {}
    # parse args
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--codes" and i + 1 < len(sys.argv):
            codes = [c.strip() for c in sys.argv[i + 1].split(",") if c.strip()]
            i += 2
            continue
        if arg == "--start" and i + 1 < len(sys.argv):
            start = sys.argv[i + 1].strip()
            i += 2
            continue
        if arg == "--end" and i + 1 < len(sys.argv):
            end = sys.argv[i + 1].strip()
            i += 2
            continue
        if arg == "--stock-start" and i + 1 < len(sys.argv):
            stock_start = sys.argv[i + 1].strip()
            i += 2
            continue
        if arg == "--stock-end" and i + 1 < len(sys.argv):
            stock_end = sys.argv[i + 1].strip()
            i += 2
            continue
        if arg == "--code-range" and i + 1 < len(sys.argv):
            # Format: CODE:YYYY-MM-DD:YYYY-MM-DD
            token = sys.argv[i + 1].strip()
            parts_token = token.split(":")
            if len(parts_token) == 3:
                c, s, e = parts_token
                code_ranges[c.strip()] = (s.strip(), e.strip())
            i += 2
            continue
        if arg == "--theme" and i + 1 < len(sys.argv):
            theme = sys.argv[i + 1].strip()
            i += 2
            continue
        if arg == "--no-ts":
            append_ts = False
            i += 1
            continue
        i += 1

    # load modules
    east = _load_module("scripts/fetch_eastmoney_cgnjj.py")
    ths = _load_module("scripts/fetch_10jqka_stock_news.py")

    # fetch base sections
    # Use date range if provided
    domestic = east.get_news_by_date_range(350, start, end)
    international = east.get_news_by_date_range(351, start, end)
    industry_reports = east.fetch_industry_reports(begin=start, end=end)

    # fetch stocks
    stock_sections = {}
    for code in codes:
        # Resolve range for this code
        rs, re = None, None
        if code in code_ranges:
            rs, re = code_ranges[code]
        elif stock_start or stock_end:
            rs = stock_start or start
            re = stock_end or (stock_start or start)
        else:
            rs, re = start, end

        if code.upper().startswith("HK"):
            hot_news = [it for it in ths.fetch_hk_news_json(code, page=1, limit=100) if it.get("date") and in_range(it["date"], rs, re)]
            related_reports = []
        else:
            url = f"https://stockpage.10jqka.com.cn/ajax/code/{code}/type/news/"
            # use module fetch_text to honor headers
            html = ths.fetch_text(url, referer=f"https://stockpage.10jqka.com.cn/{code}/news/", encoding="gbk")
            news_items, report_items = ths.parse_ashare_news_and_reports(html)
            hot_news = [it for it in news_items if it.get("date") and in_range(it["date"], rs, re)]
            related_reports = [it for it in report_items if it.get("date") and in_range(it["date"], rs, re)]
        stock_sections[code] = {"hot_news": hot_news, "related_reports": related_reports, "range_start": rs, "range_end": re}

    # Page title reflects date range
    if start == end:
        page_title = f"综合页面 · 新闻（{start}）"
    else:
        page_title = f"综合页面 · 新闻（{start} 至 {end}）"

    html = build_html_combined(domestic, international, industry_reports, stock_sections, theme=theme, page_title=page_title)

    # Determine target directory (default to Data/ when not specified)
    out_dir = os.path.dirname(out_path) or "Data"
    os.makedirs(out_dir, exist_ok=True)

    # Build timestamped output filename if enabled
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(out_path)
    if append_ts:
        if base_name.lower().endswith(".html"):
            base = base_name[: -len(".html")]
            file_name = f"{base}_{ts}.html"
        else:
            file_name = f"{base_name}_{ts}.html"
    else:
        file_name = base_name

    out_actual = os.path.join(out_dir, file_name)

    with open(out_actual, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote combined HTML to {out_actual} with {len(domestic)} domestic, {len(international)} international, {len(industry_reports)} industry, and {len(stock_sections)} stocks (theme={theme})")


if __name__ == "__main__":
    main()
