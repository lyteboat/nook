#!/usr/bin/env python3
"""生成 GitHub Pages 站点：本周简报首页、全部条目、每期雷达。

扫描 radar/YYYY/YYYY-MM-DD.html，按日期倒序排列。
- 首页（index.html）：最新一期的结论、数字，技术和产品两栏速览（按总分排），本期必看，最近几期。
- 全部条目（items.html）：汇总每期附录 A 的条目总表，可搜索，可按轨道、行业、阶段、标签筛选，可按总分排序。
- 往期（archive.html）：每期的标题、结论和必看。
- 每期页面带侧栏：上面是本期章节目录（取页面里带 id 的 h2），下面是按年、月分组的全部期数。
每期页面补上 doctype、charset、viewport、侧栏和上一期、下一期链接，正文和样式不改。
源文件不改。用法：python3 scripts/build_site.py [输出目录，默认 _site]
"""
import datetime
import html
import json
from urllib.parse import quote
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
:root{--nk-bg:#EAEEF3;--nk-ink:#141A1F;--nk-muted:#5F6A75;--nk-line:#DBE1E7;--nk-accent:#14598C;--nk-hi:#ffffff;--nk-w:272px}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--nk-bg:#111a23;--nk-ink:#E6ECF2;--nk-muted:#9AA8B6;--nk-line:#263341;--nk-accent:#7DB4E3;--nk-hi:#1B2836}}
:root[data-theme="dark"]{--nk-bg:#111a23;--nk-ink:#E6ECF2;--nk-muted:#9AA8B6;--nk-line:#263341;--nk-accent:#7DB4E3;--nk-hi:#1B2836}
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

# 每期雷达自带一套绿色主题，发布时用站点的蓝色覆盖中性色和主色，三阶段的颜色不动。
ISSUE_THEME = """<style>
[id^="i-"]{scroll-margin-top:72px}
[id^="i-"]:target{background:var(--wash);box-shadow:0 0 0 6px var(--wash);border-radius:4px}
:root{--bg:#F3F5F8;--surface:#fff;--ink:#141A1F;--muted:#5F6A75;--line:#E3E7EB;--wash:#E6EEF6;--accent:#14598C}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0D141B;--surface:#16212C;--ink:#E6ECF2;--muted:#9AA8B6;--line:#263341;--wash:#1B2836;--accent:#7DB4E3}}
:root[data-theme="dark"]{--bg:#0D141B;--surface:#16212C;--ink:#E6ECF2;--muted:#9AA8B6;--line:#263341;--wash:#1B2836;--accent:#7DB4E3}
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
        title = re.sub(r'<span class="count">.*?</span>', "", NO_RE.sub("", inner), flags=re.S)
        out.append((sid, text_of(no.group(1)) if no else "", text_of(title)))
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
             f'<li><a href="{prefix}items.html"><span>全部条目</span></a></li>'
             f'<li><a href="{prefix}archive.html"><span>往期</span></a></li></ul>']
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
    body = source[:cut] + "\n" + ISSUE_THEME + NAV_CSS + nav + source[cut:] + "\n" + pager(issues, n) + NAV_JS
    if re.match(r"\s*<!doctype", source, re.I):
        return body
    return HEAD + body + "\n</html>\n"


def digest(source):
    """从一期雷达里取首页要用的结构化内容：一句话结论、数字、本期必看、附录 A 的条目总表。

    雷达按模板写，这些块都有固定的 class；某一期缺了哪块，就跳过哪块。
    """
    m = re.search(r'<p class="thesis">(.*?)</p>', source, re.S)
    thesis = text_of(m.group(1)) if m else ""
    head = re.search(r'<div class="stats">((?:\s*<div>.*?</div>)+)', source, re.S)
    stats = [(text_of(b), text_of(s)) for b, s in
             re.findall(r'<div><b>(.*?)</b><span>(.*?)</span></div>', head.group(1) if head else "")]
    # 每个条目一句结论加六栏（What、Why、How、Who、When、Action）。必看是展开的 article，其余条目是折叠的 details。
    musts = []
    for aid, art in re.findall(r'<article class="must[^"]*" id="([^"]+)">(.*?)</article>', source, re.S):
        label = first(r'<span class="must-no">(.*?)</span>', art)
        chip = re.search(r'chip (zs|dj|sm)">(.*?)<', art)
        musts.append({
            "title": first(r"<h3>(.*?)</h3>", art), "label": label, "track": label.split(" ")[0],
            "cls": chip.group(1) if chip else "", "stage": chip.group(2) if chip else "",
            "ind": first(r'<span class="ind">(.*?)</span>', art),
            "refs": [("#" + aid, re.sub(r"^新\s*·\s*", "", first(r'<span class="name">(.*?)</span>', art)))],
            "fields": [(k, text_of(v)) for k, v in re.findall(r"<dt>(\w+)<small>.*?</small></dt>\s*<dd>(.*?)</dd>", art, re.S)],
            "src": (re.search(r'<p class="src">来源：(.*?)</p>', art, re.S) or re.search("()", "")).group(1),
        })
    concl = dict(re.findall(r'<details class="item" id="([^"]+)">\s*<summary><span class="c">(.*?)</span>', source, re.S))
    concl.update({m["refs"][0][0][1:]: m["title"] for m in musts})
    items = []
    tbl = re.search(r"条目总表.*?<thead>(.*?)</thead>.*?<tbody>(.*?)</tbody>", source, re.S)
    cols = [text_of(th) for th in re.findall(r"<th[^>]*>(.*?)</th>", tbl.group(1), re.S)] if tbl else []
    for tr in re.findall(r"<tr>(.*?)</tr>", tbl.group(2) if tbl else "", re.S):
        row = dict(zip(cols, re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)))
        if "条目" not in row:
            continue
        chip = re.search(r"chip (zs|dj|sm)", row.get("阶段", ""))
        name = text_of(row["条目"])
        # 条目单元格里的 <a href="#i-...">指向正文里讲这一条的位置，首页和全部条目页据此跳转
        anchor = re.search(r'href="(#[^"]+)"', row["条目"])
        # 早期的表头叫“方向”，还有一类“产品”，现在统一归到行业的“通用”。
        industry = text_of(row.get("行业", row.get("方向", ""))) or "通用"
        items.append({
            "date": text_of(row.get("日期", "")), "ind": industry if industry in INDUSTRIES else "通用",
            "cls": chip.group(1) if chip else "", "stage": text_of(row.get("阶段", "")),
            "name": re.sub(r"^新\s*·\s*", "", name), "new": name.startswith("新"),
            "tags": [t for t in re.split(r"[、,，/]\s*", text_of(row.get("标签", ""))) if t],
            "src": text_of(row.get("来源", "")), "anchor": anchor.group(1) if anchor else "",
            # 轨道和总分从 10-24 那期起才有，更早的期数留空
            "track": text_of(row.get("轨道", "")), "score": int(text_of(row.get("总分", "")) or 0),
            "concl": text_of(concl.get(anchor.group(1)[1:], "")) if anchor else "",
        })
    return {"thesis": thesis, "stats": stats, "musts": musts, "items": items}


INDUSTRIES = ["通用", "金融", "医疗"]
FIELD_ZH = {"What": "是什么", "Why": "为什么重要", "How": "怎么做的", "Who": "谁", "When": "何时", "Action": "我们做什么"}
TRACKS = ["技术", "产品"]

PAGE_CSS = """<style>
:root{--bg:#F3F5F8;--surface:#fff;--ink:#141A1F;--muted:#5F6A75;--line:#E3E7EB;--wash:#E6EEF6;--accent:#14598C;--on-accent:#fff;--brand:#0B2A45;--brand-ink:#DCE9F3;--brand-ink2:#8FAAC4;
--prod:#8a4b9c;--zs:#2f7d5b;--zs-bg:#e3f1ea;--dj:#3d55a3;--dj-bg:#e6eaf7;--sm:#a1701c;--sm-bg:#f6ecd8;
--f-display:"Noto Serif SC","Songti SC","SimSun",serif;--f-body:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
--f-data:"JetBrains Mono",ui-monospace,"SFMono-Regular",Menlo,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0D141B;--surface:#16212C;--ink:#E6ECF2;--muted:#9AA8B6;--line:#263341;
--wash:#1B2836;--accent:#7DB4E3;--on-accent:#0B1A27;--brand:#08121C;--prod:#d3a0e3;--zs:#6cc59a;--zs-bg:#1c3328;--dj:#9aaef0;--dj-bg:#232b45;--sm:#e0b45e;--sm-bg:#3a2f1a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0D141B;--surface:#16212C;--ink:#E6ECF2;--muted:#9AA8B6;--line:#263341;
--wash:#1B2836;--accent:#7DB4E3;--on-accent:#0B1A27;--brand:#08121C;--prod:#d3a0e3;--zs:#6cc59a;--zs-bg:#1c3328;--dj:#9aaef0;--dj-bg:#232b45;--sm:#e0b45e;--sm-bg:#3a2f1a;color-scheme:dark}
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
.topbar{background:var(--brand);margin:0 calc(-1 * max(16px,env(safe-area-inset-right,0px))) 0 calc(-1 * max(16px,env(safe-area-inset-left,0px)));
  padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px))}
.top{max-width:1080px;margin:0 auto;display:flex;align-items:center;gap:24px;padding:16px 0}
.top>a{font-family:var(--f-display);font-size:19px;font-weight:900;color:#fff;text-decoration:none}
.top nav{display:flex;gap:20px;font-size:14px;margin-left:auto}
.top nav a{color:var(--brand-ink2);text-decoration:none}.top nav a:hover{color:var(--brand-ink)}
.top nav a[aria-current]{color:#fff;font-weight:700;box-shadow:inset 0 -2px 0 #fff;padding-bottom:4px}
main{max-width:1080px;margin:0 auto;padding:40px 0 64px;display:grid;gap:52px}
.sec-h{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 14px;margin-bottom:18px}.sec-h h2{font-size:24px;font-weight:900}
.empty{color:var(--muted)}
footer{max-width:1080px;margin:0 auto;padding:0 0 40px;font-size:13px;color:var(--muted)}
/* 首页：本周简报 */
.hero{display:grid;gap:22px}
.hero h1{font-size:40px;font-weight:900;margin-top:10px}
.hero h1 a{color:inherit;text-decoration:none}.hero h1 a:hover{color:var(--accent)}
.hero-body{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:40px;align-items:start}
.thesis{font-family:var(--f-display);font-size:19px;font-weight:600;line-height:1.7;padding-left:16px;border-left:4px solid var(--accent)}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.stats div{background:var(--surface);padding:16px 18px}.stats b{display:block;font:600 28px/1.2 var(--f-data)}.stats span{font-size:12px;color:var(--muted)}
.musts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.must{background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--accent);border-radius:8px;padding:20px;display:grid;gap:12px;align-content:start}
.must .no{font:600 13px var(--f-data);color:var(--muted);display:flex;gap:8px;align-items:center}
.must h3{font-size:18px;font-weight:600}
.must dl{margin:0}.must dt{font-size:12px;font-weight:700;color:var(--muted);letter-spacing:.08em}
.must dd{margin:2px 0 10px;font-size:14px;line-height:1.7}
.must{scroll-margin-top:80px}
.must h3 a{color:inherit;text-decoration:none}.must h3 a:hover{color:var(--accent)}
.must dl.w6{display:grid;grid-template-columns:6.5em 1fr;gap:6px 12px}
.must .w6 dt{font:700 12.5px/1.7 var(--f-data);color:var(--accent);letter-spacing:0}.must.prod .w6 dt{color:var(--prod)}
.must .w6 dt small{display:block;font:400 11.5px var(--f-body);color:var(--muted)}
.must .w6 dd{margin:0}
.must .src{font-size:13px;color:var(--muted);padding-top:10px;border-top:1px dashed var(--line)}
.must .no .ind{margin-left:0}
.mustno{font-size:11px;font-weight:700;padding:1px 6px;border-radius:4px;background:var(--accent);color:var(--on-accent);text-decoration:none;margin-left:6px;white-space:nowrap}
.legend{display:flex;gap:16px;font-size:12px;color:var(--muted);align-items:center}
.legend span{display:inline-flex;gap:6px;align-items:center}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;flex:none}.dot.zs{background:var(--zs)}.dot.dj{background:var(--dj)}.dot.sm{background:var(--sm)}
.board{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.col a.item{color:inherit;text-decoration:none}.col a.item:hover{color:var(--accent);text-decoration:underline}
a.tag{text-decoration:none}a.tag:hover{color:var(--accent);border-color:var(--accent)}
.tag{display:inline-block;font-size:11px;line-height:1.5;color:var(--muted);border:1px solid var(--line);border-radius:4px;padding:0 5px;margin-left:5px;white-space:nowrap}
.col{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:16px}
.col h3{font-size:16px;font-weight:600;display:flex;justify-content:space-between;margin-bottom:10px}
.col ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.col li{display:grid;grid-template-columns:8px 1fr;gap:8px;font-size:13px;line-height:1.5}.col li .dot{margin-top:6px}
.board.two{grid-template-columns:repeat(2,minmax(0,1fr))}
.ind{font-size:11px;line-height:1.5;color:var(--accent);background:var(--wash);border-radius:4px;padding:0 5px;margin-left:5px;white-space:nowrap}
.musts.two{grid-template-columns:repeat(2,minmax(0,1fr))}
.must.prod{border-top-color:var(--prod)}.must.prod .score{color:var(--prod)}
.issues{display:grid;gap:12px}
.issue{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:18px 20px;display:grid;gap:8px}
.issue h3{font-size:20px;font-weight:900}.issue h3 a{color:inherit;text-decoration:none}.issue h3 a:hover{color:var(--accent)}
.issue p{font-size:14px}
.ms{list-style:none;margin:4px 0 0;padding:10px 0 0;border-top:1px dashed var(--line);display:grid;gap:4px;font-size:14px}
.ms .lab{display:inline-block;min-width:4.5em;font:600 12px var(--f-data);color:var(--muted)}
.ms a{color:inherit;text-decoration:none}.ms a:hover{color:var(--accent)}
.issues .m{font-family:var(--f-display);font-weight:600;color:var(--muted);margin:10px 0 0}
th.sort{cursor:pointer;color:var(--accent)}
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
th,#tb td:nth-child(-n+4),#tb td:nth-child(7),#tb td:nth-child(9){white-space:nowrap}
td.name .cc{font-weight:400;font-size:13px;color:var(--muted);margin-top:2px}
td.name a.item{color:inherit;text-decoration:none}td.name a.item:hover{color:var(--accent);text-decoration:underline}
td .tag{margin:0 4px 2px 0}
@media (max-width:900px){.hero-body,.musts,.musts.two,.board,.board.two{grid-template-columns:1fr}.hero h1{font-size:30px}.archive a{grid-template-columns:1fr;gap:2px}
  .top{gap:12px}.top nav{gap:14px}
  thead{display:none}table,tbody,tr,td{display:block}tr{border-top:1px solid var(--line);padding:8px 0}td{border:0;padding:2px 14px}}
</style>
"""


CURRENT = ' aria-current="page"'


def page(title, desc, current, body, script=""):
    nav = "".join(
        f'<a href="{href}"{CURRENT if key == current else ""}>{label}</a>'
        for key, href, label in [("home", "./", "本期"), ("items", "items.html", "全部条目"), ("archive", "archive.html", "往期")])
    return (HEAD + f"<title>{title}</title>\n"
            f'<meta name="description" content="{desc}">\n{FONTS}{PAGE_CSS}</head>\n<body>\n'
            f'<header class="topbar"><div class="top"><a href="./">Nook AI 雷达</a><nav aria-label="栏目">{nav}</nav></div></header>\n'
            f"<main>\n{body}\n</main>\n"
            f'<footer>每周三、周六更新。源文件在 <a href="https://github.com/lyteboat/nook">GitHub · lyteboat/nook</a>。</footer>\n'
            f"{script}</body>\n</html>\n")


def tag_link(t):
    return f'<a class="tag" href="items.html#tag={quote(t)}">{html.escape(t)}</a>'


def basis_html(fragment, href):
    """依据原样保留来源链接，其余标签去掉；正文内的锚点改成指向这一期。"""
    out = []
    for part in re.split(r'(<a href="[^"]*">.*?</a>)', fragment, flags=re.S):
        m = re.match(r'<a href="([^"]*)">(.*?)</a>$', part, re.S)
        if m:
            url = href + m.group(1) if m.group(1).startswith("#") else m.group(1)
            out.append(f'<a href="{html.escape(url)}">{html.escape(text_of(m.group(2)))}</a>')
        else:
            out.append(html.escape(html.unescape(re.sub(r"<[^>]+>", "", part))))
    return "".join(out)


def render_index(issues):
    if not issues:
        return page("Nook AI 雷达", "", "home", '<p class="empty">还没有雷达。</p>')
    latest = issues[0]
    dg, d = latest["digest"], latest["date"]
    href = f'radar/{latest["rel"]}'
    stats = "".join(f'<div><b>{html.escape(b)}</b><span>{html.escape(s)}</span></div>' for b, s in dg["stats"])
    thesis = f'<p class="thesis">{html.escape(dg["thesis"])}</p>' if dg["thesis"] else ""
    hero = (f'<section class="hero"><div><div class="eyebrow">本期 · {d} 周{WEEKDAYS[d.weekday()]}</div>'
            f'<h1><a href="{href}">{html.escape(latest["title"])}</a></h1></div>'
            + (f'<div class="hero-body"><div>{thesis}</div><div class="stats">{stats}</div></div>' if stats else thesis) + '</section>')
    blocks = [hero]
    labels = must_labels(dg["musts"])
    # 必看的“条目”指向速览里的条目，两边互相标出来，读者看得出必看从哪几条来
    # 两条条目可能共用一个正文锚点（比如 Skills 和 OpenShell 写在同一段），所以先按名字对，对不上再按锚点
    names = {i["name"] for i in dg["items"]}
    must_of = {}
    for n, m in enumerate(dg["musts"], 1):
        for a, t in m["refs"]:
            must_of.setdefault(t if t in names else a, []).append(n)
    if dg["items"]:
        tracked = any(i["track"] for i in dg["items"])
        groups = ([(t, sorted((i for i in dg["items"] if i["track"] == t), key=lambda i: -i["score"])) for t in TRACKS]
                  if tracked else [(t, [i for i in dg["items"] if i["ind"] == t]) for t in INDUSTRIES])
        cols = []
        for label, rows in groups:
            if not rows:
                continue
            lis = "".join(f'<li><span class="dot {i["cls"]}"></span><span>'
                          f'<a class="item" href="{href}{i["anchor"]}">{html.escape(i["concl"] or i["name"])}</a>'
                          + "".join(f'<a class="mustno" href="#must-{n}">必看 · {labels[n - 1]}</a>' for n in must_of.get(i["name"], must_of.get(i["anchor"], [])))
                          + (f'<span class="ind">{i["ind"]}</span>' if i["ind"] != "通用" else "")
                          + '</span></li>'
                          for i in rows)
            cols.append(f'<div class="col"><h3>{label}<span class="num muted">{len(rows)}</span></h3><ul>{lis}</ul></div>')
        note = '<span class="muted">每条一句结论，按重要程度排序，点开看详情</span>' if tracked else ""
        blocks.append(f'<section><div class="sec-h"><h2>本期速览</h2>{note}<div class="legend"><span><i class="dot zs"></i>招熟</span>'
                      '<span><i class="dot dj"></i>懂劲</span><span><i class="dot sm"></i>神明</span></div>'
                      f'<a href="items.html" style="margin-left:auto;font-size:14px">在全部条目里筛选 →</a></div>'
                      f'<div class="board{" two" if tracked else ""}">{"".join(cols)}</div></section>')
    if dg["musts"]:
        cards = "".join(
            f'<article class="must{" prod" if m["track"] == "产品" else ""}" id="must-{n}"><div class="no">{html.escape(labels[n - 1])}'
            + (f' <span class="chip {m["cls"]}">{html.escape(m["stage"])}</span>' if m["cls"] else "")
            + (f' <span class="ind">{html.escape(m["ind"])}</span>' if m["ind"] else "")
            + f'</div><h3><a href="{href}{m["refs"][0][0]}">{html.escape(m["title"])}</a></h3><dl class="w6">'
            + "".join(f'<dt>{k}<small>{FIELD_ZH.get(k, "")}</small></dt><dd>{html.escape(v)}</dd>' for k, v in m["fields"])
            + '</dl>' + (f'<p class="src">来源：{basis_html(m["src"], href)}</p>' if m["src"] else "") + '</article>'
            for n, m in enumerate(dg["musts"], 1))
        two = any(m["track"] for m in dg["musts"])
        sub = "技术、产品各两条，每条一句结论加六栏"
        blocks.append(f'<section id="must"><div class="sec-h"><h2>本期必看</h2>'
                      f'<span class="muted">{sub}</span></div><div class="musts{" two" if two else ""}">{cards}</div></section>')
    blocks.append(f'<section id="archive"><div class="sec-h"><h2>最近几期</h2><span class="muted">共 {len(issues)} 期</span>'
                  f'<a href="archive.html" style="margin-left:auto;font-size:14px">全部往期 →</a></div>'
                  f'<div class="archive">{archive_rows(issues[:6], "")}</div></section>')
    return page("Nook AI 雷达", "每周三、周六各一期，追踪 AI 技术和 AI 产品的关键动态。", "home", "\n".join(blocks))


def must_labels(musts):
    return [m["label"] or f"{n:02d}" for n, m in enumerate(musts, 1)]


def archive_rows(issues, prefix):
    out = []
    for (y, mth), group in by_month(issues).items():
        out.append(f'<div class="m">{y} 年 {mth} 月</div>')
        out += [f'<a href="{prefix}radar/{i["rel"]}"><span class="num muted">{i["date"]} 周{WEEKDAYS[i["date"].weekday()]}</span>'
                f'<span>{html.escape(i["title"])}</span><span class="muted">→</span></a>' for i in group]
    return "".join(out)


def render_archive(issues):
    cards = []
    for (y, mth), group in by_month(issues).items():
        cards.append(f'<div class="m">{y} 年 {mth} 月</div>')
        for i in group:
            dg, d = i["digest"], i["date"]
            href = f'radar/{i["rel"]}'
            labels = must_labels(dg["musts"])
            musts = "".join(f'<li><span class="lab">{labels[n]}</span><a href="{href}{m["refs"][0][0] if m["refs"] else ""}">'
                            f'{html.escape(m["title"])}</a></li>' for n, m in enumerate(dg["musts"]))
            counts = " · ".join(f'{t} {sum(1 for x in dg["items"] if x["track"] == t)}' for t in TRACKS
                                if any(x["track"] == t for x in dg["items"])) or f'{len(dg["items"])} 条'
            cards.append(f'<article class="issue"><div class="num muted">{d} 周{WEEKDAYS[d.weekday()]} · {counts}</div>'
                         f'<h3><a href="{href}">{html.escape(i["title"])}</a></h3>'
                         + (f'<p class="muted">{html.escape(dg["thesis"])}</p>' if dg["thesis"] else "")
                         + (f'<ul class="ms">{musts}</ul>' if musts else "") + '</article>')
    body = (f'<section class="lib-h"><div><div class="eyebrow">往期</div><h1>历期雷达</h1></div>'
            f'<div class="kpi"><div><b>{len(issues)}</b><span>期雷达</span></div></div></section>\n'
            f'<section class="issues">{"".join(cards)}</section>')
    return page("往期 · Nook AI 雷达", "历期 AI 雷达的标题、结论和必看。", "archive", body)


ITEMS_JS = """<script>
(function(){
  var D=JSON.parse(document.getElementById('data').textContent),sel={track:{},ind:{},stage:{},tag:{}},byScore=false;
  function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function ok(k,vs){var s=sel[k],any=false;vs=[].concat(vs);for(var x in s)if(s[x]){any=true;if(vs.indexOf(x)>-1)return true}return !any}
  function draw(){
    var q=document.getElementById('q').value.trim().toLowerCase();
    var rows=D.filter(function(i){return ok('track',i.track)&&ok('ind',i.ind)&&ok('stage',i.stage)&&ok('tag',i.tags)&&(!q||(i.name+' '+i.src+' '+i.tags.join(' ')).toLowerCase().indexOf(q)>-1)});
    if(byScore)rows=rows.slice().sort(function(a,b){return b.score-a.score});
    document.getElementById('count').textContent='显示 '+rows.length+' / '+D.length+' 条';
    document.getElementById('tb').innerHTML=rows.map(function(i){return '<tr><td class="num">'+e(i.date)+'</td><td>'+e(i.track||'—')+'</td><td>'+e(i.ind)+
      '</td><td><span class="chip '+i.cls+'">'+e(i.stage)+'</span></td><td class="name">'+(i.new?'<span class="new">新</span>':'')+'<a class="item" href="'+i.href+i.anchor+'">'+e(i.name)+'</a>'+(i.concl?'<div class="cc">'+e(i.concl)+'</div>':'')+
      '</td><td>'+i.tags.map(function(t){return '<a class="tag" href="#tag='+encodeURIComponent(t)+'">'+e(t)+'</a>'}).join('')+'</td><td class="num">'+(i.score||'—')+'</td><td class="muted">'+e(i.src)+'</td><td><a class="num" href="'+i.href+'">'+e(i.issue.slice(5))+'</a></td></tr>'}).join('');
  }
  [].forEach.call(document.querySelectorAll('.f'),function(b){b.addEventListener('click',function(){
    var on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',on);sel[b.dataset.k][b.dataset.v]=on;draw()})});
  function fromHash(){var m=/^#tag=(.+)$/.exec(location.hash);if(!m)return;var t=decodeURIComponent(m[1]);sel.tag={};sel.tag[t]=true;
    [].forEach.call(document.querySelectorAll('.f[data-k="tag"]'),function(b){b.setAttribute('aria-pressed',b.dataset.v===t)})}
  window.addEventListener('hashchange',function(){fromHash();draw()});
  var th=document.getElementById('bys');th.addEventListener('click',function(){byScore=!byScore;th.textContent=byScore?'总分 ↓':'总分';draw()});
  document.getElementById('q').addEventListener('input',draw);fromHash();draw();
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
            f'<div><b>{len(tags)}</b><span>个标签</span></div></div></section>\n'
            '<section><div class="filters">'
            '<input id="q" type="search" placeholder="搜索条目、标签或来源，比如 RAG、FSB、medRxiv" aria-label="搜索">'
            f'<div class="row"><span class="lab">轨道</span>{chips("track", [(x, x) for x in TRACKS])}</div>'
            f'<div class="row"><span class="lab">行业</span>{chips("ind", [(x, x) for x in INDUSTRIES])}</div>'
            f'<div class="row"><span class="lab">阶段</span>{chips("stage", [("招熟", "招熟"), ("懂劲", "懂劲"), ("神明", "神明")])}'
            '<span class="count" id="count"></span></div>'
            f'<div class="row"><span class="lab">标签</span>{chips("tag", [(t, f"{t} <span class=num>{counts[t]}</span>") for t in tags])}</div></div>'
            '<table><thead><tr><th>日期</th><th>轨道</th><th>行业</th><th>阶段</th><th>条目</th><th>标签</th>'
            '<th class="sort" id="bys" title="点一下按总分从高到低排">总分</th><th>来源</th><th>所在期</th></tr></thead>'
            '<tbody id="tb"></tbody></table></section>\n'
            f'<script type="application/json" id="data">{data}</script>')
    return page("全部条目 · Nook AI 雷达", "历期 AI 雷达的全部条目，可按轨道、行业、阶段、标签筛选。", "items", body, ITEMS_JS)


def main():
    issues = collect()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("")
    (OUT / "index.html").write_text(render_index(issues), encoding="utf-8")
    (OUT / "items.html").write_text(render_items(issues), encoding="utf-8")
    (OUT / "archive.html").write_text(render_archive(issues), encoding="utf-8")
    for n, i in enumerate(issues):
        dest = OUT / "radar" / i["rel"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(wrap_page(issues, n), encoding="utf-8")
    print(f"站点已生成：{OUT}，共 {len(issues)} 期雷达")


if __name__ == "__main__":
    main()
