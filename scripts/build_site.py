#!/usr/bin/env python3
"""生成 GitHub Pages 站点：本周简报首页、全部条目、每期雷达。

扫描 radar/YYYY/YYYY-MM-DD.html，按日期倒序排列。
- 首页（index.html）：最新一期的结论、数字、本期必懂、按行业分栏的速览，下面是往期。
- 全部条目（items.html）：汇总每期附录 A 的条目总表，可搜索，可按行业、阶段、技术标签筛选。
- 每期页面带侧栏：上面是本期章节目录（取页面里带 id 的 h2），下面是按年、月分组的全部期数。
每期页面补上 doctype、charset、viewport、侧栏和上一期、下一期链接，正文和样式不改。
源文件不改。用法：python3 scripts/build_site.py [输出目录，默认 _site]
"""
import datetime
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RADAR = ROOT / "radar"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "_site")

WEEKDAYS = "一二三四五六日"
NAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.html$")
H2_RE = re.compile(r'<h2[^>]*\bid="([^"]+)"[^>]*>(.*?)</h2>', re.S)
NO_RE = re.compile(r'<span class="no">(.*?)</span>', re.S)
HEAD = (
    '<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
)
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;900'
    '&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap">\n'
)

# 侧栏样式和脚本：类名、变量都加 nk 前缀，不和雷达页面自己的样式冲突。
NAV_CSS = """<style>
:root{--nk-bg:#eef1ef;--nk-ink:#1b2321;--nk-muted:#5d6966;--nk-line:#dde2df;--nk-accent:#1f5f58;--nk-hi:#ffffff;--nk-w:272px}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--nk-bg:#171d1b;--nk-ink:#e3e9e6;--nk-muted:#9aa6a2;--nk-line:#2c3532;--nk-accent:#6fc1b5;--nk-hi:#202825}}
:root[data-theme="dark"]{--nk-bg:#171d1b;--nk-ink:#e3e9e6;--nk-muted:#9aa6a2;--nk-line:#2c3532;--nk-accent:#6fc1b5;--nk-hi:#202825}
html{scroll-padding-top:16px}
.nk-side{position:fixed;inset:0 auto 0 0;width:var(--nk-w);z-index:50;background:var(--nk-bg);border-right:1px solid var(--nk-line);
  overflow-y:auto;padding:22px 18px 40px;font:14px/1.6 "Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;color:var(--nk-ink);
  box-sizing:border-box}
.nk-side *{box-sizing:border-box}
.nk-side a{color:inherit;text-decoration:none}
.nk-brand{display:block;font-family:"Noto Serif SC","Songti SC",serif;font-weight:900;font-size:19px;margin-bottom:18px}
.nk-label{font:600 11px/1 "JetBrains Mono",ui-monospace,monospace;letter-spacing:.14em;color:var(--nk-muted);margin:22px 0 8px;text-transform:uppercase}
.nk-side ul{list-style:none;margin:0;padding:0}
.nk-toc a,.nk-issues a{display:flex;gap:8px;padding:5px 10px;border-radius:5px;border-left:2px solid transparent}
.nk-toc a:hover,.nk-issues a:hover{background:var(--nk-hi)}
.nk-toc a.on{border-left-color:var(--nk-accent);color:var(--nk-accent);background:var(--nk-hi);font-weight:500}
.nk-toc .n{font:12px/1.9 "JetBrains Mono",ui-monospace,monospace;color:var(--nk-muted);min-width:1.6em}
.nk-year{font-weight:700;margin:10px 0 2px;padding-left:10px}
.nk-month{font-size:12px;color:var(--nk-muted);margin:6px 0 2px;padding-left:10px}
.nk-issues a{flex-direction:column;gap:0}
.nk-issues .d{font:12px/1.6 "JetBrains Mono",ui-monospace,monospace;color:var(--nk-muted)}
.nk-issues .t{font-size:13px;line-height:1.5}
.nk-issues a.cur{background:var(--nk-hi);border-left-color:var(--nk-accent)}
.nk-issues a.cur .t{color:var(--nk-accent);font-weight:500}
.nk-bar{display:none}
.nk-pager{max-width:880px;margin:0 auto 56px;display:grid;grid-template-columns:1fr 1fr;gap:12px;
  font:14px/1.5 "Noto Sans SC","PingFang SC",system-ui,sans-serif}
.nk-pager a{display:grid;gap:2px;padding:12px 16px;border:1px solid var(--nk-line);border-radius:6px;color:var(--nk-ink);text-decoration:none}
.nk-pager a:hover{border-color:var(--nk-accent)}
.nk-pager .next{grid-column:2;text-align:right}
.nk-pager small{color:var(--nk-muted);font-size:12px}
@media (min-width:1080px){body{padding-left:calc(var(--nk-w) + 24px)!important}}
@media (max-width:1079px){
  html{scroll-padding-top:64px}
  .nk-side{transform:translateX(-100%);transition:transform .2s ease;box-shadow:0 0 0 100vmax transparent}
  .nk-open .nk-side{transform:none;box-shadow:0 0 0 100vmax rgba(0,0,0,.35)}
  .nk-bar{display:flex;position:sticky;top:0;z-index:40;align-items:center;gap:12px;margin:0 -16px;padding:10px 16px;
    background:var(--nk-bg);border-bottom:1px solid var(--nk-line);font:14px/1.4 "Noto Sans SC",system-ui,sans-serif}
  .nk-bar button{font:inherit;color:var(--nk-ink);background:none;border:1px solid var(--nk-line);border-radius:5px;padding:4px 12px;cursor:pointer}
  .nk-bar a{color:var(--nk-ink);text-decoration:none;font-weight:700}
}
@media (max-width:560px){.nk-pager{grid-template-columns:1fr}.nk-pager .next{grid-column:1}}
</style>
"""

NAV_JS = """<script>
(function(){
  var root=document.documentElement,btn=document.querySelector('.nk-bar button');
  if(btn)btn.addEventListener('click',function(e){e.stopPropagation();root.classList.toggle('nk-open')});
  document.addEventListener('click',function(e){
    if(root.classList.contains('nk-open')&&(!e.target.closest('.nk-side')||e.target.closest('a')))root.classList.remove('nk-open')});
  var links=[].slice.call(document.querySelectorAll('.nk-toc a'));
  if(!links.length||!('IntersectionObserver' in window))return;
  var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a});
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){links.forEach(function(a){a.classList.remove('on')});map[e.target.id].classList.add('on')}})},
    {rootMargin:'0px 0px -70% 0px'});
  Object.keys(map).forEach(function(id){var el=document.getElementById(id);if(el)io.observe(el)});
})();
</script>
"""


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def first(pattern, source):
    m = re.search(pattern, source, re.S)
    return text_of(m.group(1)) if m else ""


def sections(source):
    out = []
    for sid, inner in H2_RE.findall(source):
        no = NO_RE.search(inner)
        out.append((sid, text_of(no.group(1)) if no else "", text_of(NO_RE.sub("", inner))))
    return out


def collect():
    issues = []
    for path in sorted(RADAR.glob("*/*.html")):
        m = NAME_RE.match(path.name)
        if not m:
            continue
        date = datetime.date(*map(int, m.groups()))
        source = path.read_text(encoding="utf-8")
        issues.append({
            "date": date,
            "rel": path.relative_to(RADAR).as_posix(),
            "title": first(r"<h1[^>]*>(.*?)</h1>", source) or f"Nook 雷达 {date}",
            "sections": sections(source),
            "digest": digest(source),
            "source": source,
        })
    issues.sort(key=lambda i: i["date"], reverse=True)
    return issues


def by_month(issues):
    groups = {}
    for i in issues:
        groups.setdefault((i["date"].year, i["date"].month), []).append(i)
    return groups


def sidebar(issues, prefix, current=None):
    """prefix 是从当前页面回到站点根目录的相对路径。"""
    parts = [f'<a class="nk-brand" href="{prefix}">Nook AI 雷达</a>',
             f'<ul class="nk-toc"><li><a href="{prefix}"><span>本期简报</span></a></li>'
             f'<li><a href="{prefix}items.html"><span>全部条目</span></a></li></ul>']
    if current and current["sections"]:
        parts.append('<div class="nk-label">本期目录</div><ul class="nk-toc">')
        for sid, no, title in current["sections"]:
            parts.append(f'<li><a href="#{html.escape(sid)}"><span class="n">{html.escape(no)}</span>'
                         f'<span>{html.escape(title)}</span></a></li>')
        parts.append("</ul>")
    parts.append('<div class="nk-label">全部期数</div><ul class="nk-issues">')
    year = None
    for (y, mth), group in by_month(issues).items():
        if y != year:
            parts.append(f'<li class="nk-year">{y} 年</li>')
            year = y
        parts.append(f'<li class="nk-month">{mth} 月</li>')
        for i in group:
            cur = ' class="cur" aria-current="page"' if i is current else ""
            d = i["date"]
            parts.append(f'<li><a href="{prefix}radar/{i["rel"]}"{cur}><span class="d">{d:%m-%d} 周{WEEKDAYS[d.weekday()]}</span>'
                         f'<span class="t">{html.escape(i["title"])}</span></a></li>')
    parts.append("</ul>")
    bar = (f'<div class="nk-bar"><button type="button" aria-label="打开目录">☰ 目录</button>'
           f'<a href="{prefix}">Nook AI 雷达</a></div>\n')
    return bar + '<nav class="nk-side" aria-label="站点目录">' + "\n".join(parts) + "</nav>\n"


def pager(issues, n):
    """issues 按日期倒序：n-1 是更新的一期，n+1 是更早的一期。"""
    links = []
    if n + 1 < len(issues):
        i = issues[n + 1]
        links.append(f'<a href="../../radar/{i["rel"]}"><small>← 上一期 {i["date"]}</small>{html.escape(i["title"])}</a>')
    if n > 0:
        i = issues[n - 1]
        links.append(f'<a class="next" href="../../radar/{i["rel"]}"><small>下一期 {i["date"]} →</small>{html.escape(i["title"])}</a>')
    return f'<nav class="nk-pager" aria-label="翻页">{"".join(links)}</nav>\n' if links else ""


def wrap_page(issues, n):
    """雷达是不带 <html>/<head> 的片段：补上骨架，在样式之后插入侧栏，末尾加翻页。"""
    issue = issues[n]
    source = issue["source"]
    nav = sidebar(issues, "../../", issue)
    cut = source.rfind("</style>")
    cut = cut + len("</style>") if cut != -1 else 0
    body = source[:cut] + "\n" + NAV_CSS + nav + source[cut:] + "\n" + pager(issues, n) + NAV_JS
    if re.match(r"\s*<!doctype", source, re.I):
        return body
    return HEAD + body + "\n</html>\n"


def digest(source):
    """从一期雷达里取首页要用的结构化内容：一句话结论、数字、本期必懂、附录 A 的条目总表。

    雷达按模板写，这些块都有固定的 class；某一期缺了哪块，就跳过哪块。
    """
    m = re.search(r'<p class="thesis">(.*?)</p>', source, re.S)
    thesis = text_of(m.group(1)) if m else ""
    head = re.search(r'<div class="stats">((?:\s*<div>.*?</div>)+)', source, re.S)
    stats = [(text_of(b), text_of(s)) for b, s in
             re.findall(r'<div><b>(.*?)</b><span>(.*?)</span></div>', head.group(1) if head else "")]
    musts = []
    for art in re.findall(r'<article class="must">(.*?)</article>', source, re.S):
        h3 = re.search(r"<h3>(.*?)</h3>", art, re.S)
        if not h3:
            continue
        chip = re.search(r'chip (zs|dj|sm)">(.*?)<', h3.group(1))
        kv = dict((text_of(k), text_of(v)) for k, v in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", art, re.S))
        musts.append({
            "title": text_of(re.sub(r'<span class="chip.*?</span>', "", h3.group(1))),
            "cls": chip.group(1) if chip else "", "stage": chip.group(2) if chip else "",
            "xinfa": kv.get("心法", ""), "zhaoshi": kv.get("招式", ""),
        })
    items = []
    tbl = re.search(r"条目总表.*?<thead>(.*?)</thead>.*?<tbody>(.*?)</tbody>", source, re.S)
    cols = [text_of(th) for th in re.findall(r"<th[^>]*>(.*?)</th>", tbl.group(1), re.S)] if tbl else []
    for tr in re.findall(r"<tr>(.*?)</tr>", tbl.group(2) if tbl else "", re.S):
        row = dict(zip(cols, re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)))
        if "条目" not in row:
            continue
        chip = re.search(r"chip (zs|dj|sm)", row.get("阶段", ""))
        name = text_of(row["条目"])
        # 早期的表头叫“方向”，还有一类“产品”，现在统一归到行业的“通用”。
        industry = text_of(row.get("行业", row.get("方向", ""))) or "通用"
        items.append({
            "date": text_of(row.get("日期", "")), "ind": industry if industry in INDUSTRIES else "通用",
            "cls": chip.group(1) if chip else "", "stage": text_of(row.get("阶段", "")),
            "name": re.sub(r"^新\s*·\s*", "", name), "new": name.startswith("新"),
            "tags": [t for t in re.split(r"[、,，/]\s*", text_of(row.get("标签", ""))) if t],
            "src": text_of(row.get("来源", "")),
        })
    return {"thesis": thesis, "stats": stats, "musts": musts, "items": items}


INDUSTRIES = ["通用", "金融", "医疗"]

PAGE_CSS = """<style>
:root{--bg:#f6f7f5;--surface:#fff;--ink:#1b2321;--muted:#5d6966;--line:#dde2df;--wash:#eef1ef;--accent:#1f5f58;--on-accent:#fff;
--zs:#2f7d5b;--zs-bg:#e3f1ea;--dj:#3d55a3;--dj-bg:#e6eaf7;--sm:#a1701c;--sm-bg:#f6ecd8;
--f-display:"Noto Serif SC","Songti SC","SimSun",serif;--f-body:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
--f-data:"JetBrains Mono",ui-monospace,"SFMono-Regular",Menlo,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#121715;--surface:#1a201e;--ink:#e3e9e6;--muted:#9aa6a2;--line:#2c3532;
--wash:#202825;--accent:#6fc1b5;--on-accent:#0f1513;--zs:#6cc59a;--zs-bg:#1c3328;--dj:#9aaef0;--dj-bg:#232b45;--sm:#e0b45e;--sm-bg:#3a2f1a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121715;--surface:#1a201e;--ink:#e3e9e6;--muted:#9aa6a2;--line:#2c3532;
--wash:#202825;--accent:#6fc1b5;--on-accent:#0f1513;--zs:#6cc59a;--zs-bg:#1c3328;--dj:#9aaef0;--dj-bg:#232b45;--sm:#e0b45e;--sm-bg:#3a2f1a;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 var(--f-body);
  padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px))}
a{color:var(--accent)}
h1,h2,h3{font-family:var(--f-display);margin:0;line-height:1.35}
p{margin:0}
.num{font-family:var(--f-data);font-variant-numeric:tabular-nums}
.muted{color:var(--muted)}
.eyebrow{font:600 12px/1.4 var(--f-data);letter-spacing:.14em;color:var(--muted);text-transform:uppercase}
.chip{display:inline-flex;font-size:12px;font-weight:700;padding:1px 9px;border-radius:999px;white-space:nowrap;letter-spacing:.04em}
.zs{color:var(--zs);background:var(--zs-bg)}.dj{color:var(--dj);background:var(--dj-bg)}.sm{color:var(--sm);background:var(--sm-bg)}
.new{font-size:11px;font-weight:700;color:var(--accent);margin-right:5px}
.top{max-width:1080px;margin:0 auto;display:flex;align-items:center;gap:24px;padding:18px 0;border-bottom:1px solid var(--line)}
.top>a{font-family:var(--f-display);font-size:19px;font-weight:900;color:var(--ink);text-decoration:none}
.top nav{display:flex;gap:20px;font-size:14px;margin-left:auto}
.top nav a{color:var(--muted);text-decoration:none}.top nav a[aria-current]{color:var(--ink);font-weight:700}
main{max-width:1080px;margin:0 auto;padding:40px 0 64px;display:grid;gap:52px}
.sec-h{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 14px;margin-bottom:18px}.sec-h h2{font-size:24px;font-weight:900}
.empty{color:var(--muted)}
footer{max-width:1080px;margin:0 auto;padding:0 0 40px;font-size:13px;color:var(--muted)}
/* 首页：本周简报 */
.hero{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:40px;align-items:end}
.hero h1{font-size:40px;font-weight:900;margin:10px 0 18px}
.thesis{font-family:var(--f-display);font-size:19px;font-weight:600;line-height:1.7;padding-left:16px;border-left:4px solid var(--accent)}
.cta{display:flex;gap:12px;margin-top:22px;flex-wrap:wrap}
.btn{display:inline-block;padding:9px 18px;border-radius:6px;text-decoration:none;font-weight:700;font-size:14px}
.btn.pri{background:var(--accent);color:var(--on-accent)}.btn.sec{border:1px solid var(--line);color:var(--ink);background:var(--surface)}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.stats div{background:var(--surface);padding:16px 18px}.stats b{display:block;font:600 28px/1.2 var(--f-data)}.stats span{font-size:12px;color:var(--muted)}
.musts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.must{background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--accent);border-radius:8px;padding:20px;display:grid;gap:12px;align-content:start}
.must .no{font:600 13px var(--f-data);color:var(--muted);display:flex;gap:8px;align-items:center}
.must h3{font-size:18px;font-weight:600}
.must dl{margin:0}.must dt{font-size:12px;font-weight:700;color:var(--muted);letter-spacing:.08em}
.must dd{margin:2px 0 10px;font-size:14px;line-height:1.7}
.must .more{font-size:13px}
.legend{display:flex;gap:16px;font-size:12px;color:var(--muted);align-items:center}
.legend span{display:inline-flex;gap:6px;align-items:center}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;flex:none}.dot.zs{background:var(--zs)}.dot.dj{background:var(--dj)}.dot.sm{background:var(--sm)}
.board{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.tag{display:inline-block;font-size:11px;line-height:1.5;color:var(--muted);border:1px solid var(--line);border-radius:4px;padding:0 5px;margin-left:5px;white-space:nowrap}
.col{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:16px}
.col h3{font-size:16px;font-weight:600;display:flex;justify-content:space-between;margin-bottom:10px}
.col ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.col li{display:grid;grid-template-columns:8px 1fr;gap:8px;font-size:13px;line-height:1.5}.col li .dot{margin-top:6px}
.archive{display:grid;gap:8px}
.archive a{display:grid;grid-template-columns:10em 1fr auto;gap:16px;padding:12px 16px;background:var(--surface);border:1px solid var(--line);border-radius:6px;color:inherit;text-decoration:none}
.archive a:hover{border-color:var(--accent)}
.archive .m{font-family:var(--f-display);font-weight:600;color:var(--muted);margin:10px 0 2px}
/* 全部条目 */
.kpi{display:flex;gap:28px}.kpi div{display:grid}.kpi b{font:600 26px/1.2 var(--f-data)}.kpi span{font-size:12px;color:var(--muted)}
.lib-h{display:flex;justify-content:space-between;align-items:end;gap:24px;flex-wrap:wrap;border-bottom:2px solid var(--ink);padding-bottom:20px}
.lib-h h1{font-size:34px;font-weight:900;margin-top:8px}
.filters{display:grid;gap:10px;position:sticky;top:0;z-index:5;background:var(--bg);padding:12px 0;border-bottom:1px solid var(--line)}
.filters input{width:100%;font:inherit;padding:9px 14px;border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--ink)}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:13px}
.row .lab{color:var(--muted);width:3em}
.f{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:2px 12px;cursor:pointer}
.f[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.f .num{font-size:11px;opacity:.6;margin-left:2px}
.count{font-size:13px;color:var(--muted);margin-left:auto}
table{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--line);font-size:14px}
th{text-align:left;font-size:12px;color:var(--muted);font-weight:600;background:var(--wash);padding:10px 14px}
td{padding:11px 14px;border-top:1px solid var(--line);vertical-align:top}
td.name{font-weight:500}
td .tag{margin:0 4px 2px 0}
@media (max-width:900px){.hero,.musts,.board{grid-template-columns:1fr}.hero h1{font-size:30px}.archive a{grid-template-columns:1fr;gap:2px}
  .top{gap:12px}.top nav{gap:14px}
  thead{display:none}table,tbody,tr,td{display:block}tr{border-top:1px solid var(--line);padding:8px 0}td{border:0;padding:2px 14px}}
</style>
"""


CURRENT = ' aria-current="page"'


def page(title, desc, current, body, script=""):
    nav = "".join(
        f'<a href="{href}"{CURRENT if key == current else ""}>{label}</a>'
        for key, href, label in [("home", "./", "本期"), ("items", "items.html", "全部条目"), ("archive", "./#archive", "往期")])
    return (HEAD + f"<title>{title}</title>\n"
            f'<meta name="description" content="{desc}">\n{FONTS}{PAGE_CSS}</head>\n<body>\n'
            f'<div class="top"><a href="./">Nook AI 雷达</a><nav aria-label="栏目">{nav}</nav></div>\n'
            f"<main>\n{body}\n</main>\n"
            f'<footer>每周三、周六更新。源文件在 <a href="https://github.com/lyteboat/nook">GitHub · lyteboat/nook</a>。</footer>\n'
            f"{script}</body>\n</html>\n")


def render_index(issues):
    if not issues:
        return page("Nook AI 雷达", "", "home", '<p class="empty">还没有雷达。</p>')
    latest = issues[0]
    dg, d = latest["digest"], latest["date"]
    href = f'radar/{latest["rel"]}'
    stats = "".join(f'<div><b>{html.escape(b)}</b><span>{html.escape(s)}</span></div>' for b, s in dg["stats"])
    thesis = f'<p class="thesis">{html.escape(dg["thesis"])}</p>' if dg["thesis"] else ""
    hero = (f'<section class="hero"><div><div class="eyebrow">本期 · {d} 周{WEEKDAYS[d.weekday()]}</div>'
            f'<h1>{html.escape(latest["title"])}</h1>{thesis}'
            f'<div class="cta"><a class="btn pri" href="{href}">读完整一期</a>'
            + ('<a class="btn sec" href="#must">只读 3 分钟版</a>' if dg["musts"] else "")
            + f'</div></div>{f"<div class=stats>{stats}</div>" if stats else ""}</section>')
    blocks = [hero]
    if dg["musts"]:
        cards = "".join(
            f'<article class="must"><div class="no">{n:02d}'
            + (f' <span class="chip {m["cls"]}">{html.escape(m["stage"])}</span>' if m["cls"] else "")
            + f'</div><h3>{html.escape(m["title"])}</h3><dl>'
            + (f'<dt>心法</dt><dd>{html.escape(m["xinfa"])}</dd>' if m["xinfa"] else "")
            + (f'<dt>招式</dt><dd>{html.escape(m["zhaoshi"])}</dd>' if m["zhaoshi"] else "")
            + f'</dl><a class="more" href="{href}#s-must">看依据和来源 →</a></article>'
            for n, m in enumerate(dg["musts"], 1))
        blocks.append(f'<section id="must"><div class="sec-h"><h2>本期必懂</h2>'
                      f'<span class="muted">只读这几条，也能抓住本期八成的价值</span></div><div class="musts">{cards}</div></section>')
    if dg["items"]:
        cols = []
        for label in INDUSTRIES:
            rows = [i for i in dg["items"] if i["ind"] == label]
            if not rows:
                continue
            lis = "".join(f'<li><span class="dot {i["cls"]}"></span><span>{"<span class=new>新</span>" if i["new"] else ""}'
                          f'{html.escape(i["name"])}{"".join(f"<span class=tag>{html.escape(t)}</span>" for t in i["tags"])}</span></li>'
                          for i in rows)
            cols.append(f'<div class="col"><h3>{label}<span class="num muted">{len(rows)}</span></h3><ul>{lis}</ul></div>')
        blocks.append('<section><div class="sec-h"><h2>本期速览</h2><div class="legend"><span><i class="dot zs"></i>招熟</span>'
                      '<span><i class="dot dj"></i>懂劲</span><span><i class="dot sm"></i>神明</span></div>'
                      f'<a href="items.html" style="margin-left:auto;font-size:14px">在全部条目里筛选 →</a></div>'
                      f'<div class="board">{"".join(cols)}</div></section>')
    arch = []
    for (y, mth), group in by_month(issues).items():
        arch.append(f'<div class="m">{y} 年 {mth} 月</div>')
        arch += [f'<a href="radar/{i["rel"]}"><span class="num muted">{i["date"]} 周{WEEKDAYS[i["date"].weekday()]}</span>'
                 f'<span>{html.escape(i["title"])}</span><span class="muted">→</span></a>' for i in group]
    blocks.append(f'<section id="archive"><div class="sec-h"><h2>往期</h2><span class="muted">共 {len(issues)} 期</span></div>'
                  f'<div class="archive">{"".join(arch)}</div></section>')
    return page("Nook AI 雷达", "每周三、周六各一期，追踪 AI 模型、Agent、数据与行业落地的关键动态。", "home", "\n".join(blocks))


ITEMS_JS = """<script>
(function(){
  var D=JSON.parse(document.getElementById('data').textContent),sel={ind:{},stage:{},tag:{}};
  function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function ok(k,vs){var s=sel[k],any=false;vs=[].concat(vs);for(var x in s)if(s[x]){any=true;if(vs.indexOf(x)>-1)return true}return !any}
  function draw(){
    var q=document.getElementById('q').value.trim().toLowerCase();
    var rows=D.filter(function(i){return ok('ind',i.ind)&&ok('stage',i.stage)&&ok('tag',i.tags)&&(!q||(i.name+' '+i.src+' '+i.tags.join(' ')).toLowerCase().indexOf(q)>-1)});
    document.getElementById('count').textContent='显示 '+rows.length+' / '+D.length+' 条';
    document.getElementById('tb').innerHTML=rows.map(function(i){return '<tr><td class="num">'+e(i.date)+'</td><td>'+e(i.ind)+
      '</td><td><span class="chip '+i.cls+'">'+e(i.stage)+'</span></td><td class="name">'+(i.new?'<span class="new">新</span>':'')+e(i.name)+
      '</td><td>'+i.tags.map(function(t){return '<span class="tag">'+e(t)+'</span>'}).join('')+'</td><td class="muted">'+e(i.src)+'</td><td><a class="num" href="'+i.href+'">'+e(i.issue.slice(5))+'</a></td></tr>'}).join('');
  }
  [].forEach.call(document.querySelectorAll('.f'),function(b){b.addEventListener('click',function(){
    var on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',on);sel[b.dataset.k][b.dataset.v]=on;draw()})});
  document.getElementById('q').addEventListener('input',draw);draw();
})();
</script>
"""


def render_items(issues):
    items = []
    for i in issues:
        items += [dict(x, issue=str(i["date"]), href=f'radar/{i["rel"]}') for x in i["digest"]["items"]]
    counts = {}
    for x in items:
        for t in x["tags"]:
            counts[t] = counts.get(t, 0) + 1
    tags = sorted(counts, key=lambda t: (-counts[t], t))

    def chips(key, vals):
        return "".join(f'<button type="button" class="f" aria-pressed="false" data-k="{key}" data-v="{v}">{lab}</button>' for v, lab in vals)

    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    body = (f'<section class="lib-h"><div><div class="eyebrow">全部条目</div><h1>历期雷达条目总表</h1></div>'
            f'<div class="kpi"><div><b>{len(issues)}</b><span>期雷达</span></div><div><b>{len(items)}</b><span>个条目</span></div>'
            f'<div><b>{len(tags)}</b><span>个技术标签</span></div></div></section>\n'
            '<section><div class="filters">'
            '<input id="q" type="search" placeholder="搜索条目、标签或来源，比如 RAG、FSB、medRxiv" aria-label="搜索">'
            f'<div class="row"><span class="lab">行业</span>{chips("ind", [(x, x) for x in INDUSTRIES])}</div>'
            f'<div class="row"><span class="lab">阶段</span>{chips("stage", [("招熟", "招熟"), ("懂劲", "懂劲"), ("神明", "神明")])}'
            '<span class="count" id="count"></span></div>'
            f'<div class="row"><span class="lab">标签</span>{chips("tag", [(t, f"{t} <span class=num>{counts[t]}</span>") for t in tags])}</div></div>'
            '<table><thead><tr><th>日期</th><th>行业</th><th>阶段</th><th>条目</th><th>标签</th><th>来源</th><th>所在期</th></tr></thead>'
            '<tbody id="tb"></tbody></table></section>\n'
            f'<script type="application/json" id="data">{data}</script>')
    return page("全部条目 · Nook AI 雷达", "历期 AI 雷达的全部条目，可按行业、阶段、技术标签筛选。", "items", body, ITEMS_JS)


def main():
    issues = collect()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("")
    (OUT / "index.html").write_text(render_index(issues), encoding="utf-8")
    (OUT / "items.html").write_text(render_items(issues), encoding="utf-8")
    for n, i in enumerate(issues):
        dest = OUT / "radar" / i["rel"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(wrap_page(issues, n), encoding="utf-8")
    print(f"站点已生成：{OUT}，共 {len(issues)} 期雷达")


if __name__ == "__main__":
    main()
