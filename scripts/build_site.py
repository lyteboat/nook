#!/usr/bin/env python3
"""生成 GitHub Pages 站点：雷达首页 + 每期雷达，带侧栏目录导航。

扫描 radar/YYYY/YYYY-MM-DD.html，按日期倒序生成首页。首页和每期页面共用一个侧栏：
上面是当前这一期的章节目录（取页面里带 id 的 h2），下面是按年、月分组的全部期数。
每期页面补上 doctype、charset、viewport、侧栏和上一期、下一期链接，正文和样式不改。
源文件不改。用法：python3 scripts/build_site.py [输出目录，默认 _site]
"""
import datetime
import html
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
    parts = [f'<a class="nk-brand" href="{prefix}">Nook AI 雷达</a>']
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


def render_index(issues):
    blocks = []
    for (y, mth), group in by_month(issues).items():
        rows = []
        for i in group:
            d = i["date"]
            latest = i is issues[0]
            badge = '<span class="badge">最新</span>' if latest else ""
            rows.append(
                f'<li class="{"issue latest" if latest else "issue"}"><a href="radar/{i["rel"]}">'
                f'<span class="date num">{d:%Y-%m-%d}<small>周{WEEKDAYS[d.weekday()]}</small></span>'
                f'<span class="title">{html.escape(i["title"])}{badge}</span></a></li>'
            )
        blocks.append(f'<section><h2 id="m-{y}-{mth:02d}">{y} 年 {mth} 月</h2><ol>{"".join(rows)}</ol></section>')
    body = "\n".join(blocks) if blocks else '<p class="empty">还没有雷达。</p>'
    updated = issues[0]["date"].isoformat() if issues else "—"
    return (INDEX.replace("{{FONTS}}", FONTS).replace("{{NAV_CSS}}", NAV_CSS)
            .replace("{{NAV}}", sidebar(issues, "./")).replace("{{NAV_JS}}", NAV_JS)
            .replace("{{ISSUES}}", body).replace("{{COUNT}}", str(len(issues))).replace("{{UPDATED}}", updated))


INDEX = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nook AI 雷达</title>
<meta name="description" content="每周三、周六各一期，追踪 AI 模型、Agent、数据与行业落地的关键动态。">
{{FONTS}}<style>
:root{
  --bg:#f6f7f5; --surface:#ffffff; --ink:#1b2321; --muted:#5d6966; --line:#dde2df; --wash:#eef1ef; --accent:#1f5f58;
  --f-display:"Noto Serif SC","Songti SC","SimSun",serif;
  --f-body:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
  --f-data:"JetBrains Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121715; --surface:#1a201e; --ink:#e3e9e6; --muted:#9aa6a2; --line:#2c3532; --wash:#202825; --accent:#6fc1b5; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121715; --surface:#1a201e; --ink:#e3e9e6; --muted:#9aa6a2; --line:#2c3532; --wash:#202825; --accent:#6fc1b5; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.75;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.wrap{max-width:880px;margin:0 auto;padding-block:48px 64px;display:grid;gap:32px}
header{display:grid;gap:12px;border-bottom:2px solid var(--ink);padding-bottom:22px}
.eyebrow{font-family:var(--f-data);font-size:12px;letter-spacing:.14em;color:var(--muted);text-transform:uppercase}
h1{font-family:var(--f-display);font-size:34px;font-weight:900;margin:0;line-height:1.35}
h2{font-family:var(--f-display);font-size:18px;font-weight:600;margin:0 0 12px;color:var(--muted)}
header p{margin:0;color:var(--muted)}
.meta{display:flex;flex-wrap:wrap;gap:6px 22px;font-size:13px;color:var(--muted)}
.num{font-family:var(--f-data);font-variant-numeric:tabular-nums}
ol{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.issue a{display:grid;grid-template-columns:8.5em 1fr;gap:16px;align-items:baseline;padding:14px 18px;
  background:var(--surface);border:1px solid var(--line);border-radius:6px;color:inherit;text-decoration:none}
.issue a:hover{border-color:var(--accent)}
.issue a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.latest a{border-left:4px solid var(--accent);padding-block:20px}
.latest .title{font-size:20px}
.date{font-size:13px;color:var(--muted);display:flex;gap:8px}
.date small{font-family:var(--f-body)}
.title{font-family:var(--f-display);font-size:17px;font-weight:600;line-height:1.5}
.badge{display:inline-block;margin-left:10px;font-family:var(--f-body);font-size:12px;font-weight:700;color:var(--accent);
  background:var(--wash);border-radius:999px;padding:0 9px;vertical-align:3px}
.empty{color:var(--muted)}
footer{font-size:13px;color:var(--muted)}
footer a{color:var(--accent)}
@media (max-width:560px){.issue a{grid-template-columns:1fr;gap:4px} h1{font-size:28px}}
</style>
{{NAV_CSS}}</head>
<body>
{{NAV}}<div class="wrap">
<header>
  <div class="eyebrow">Nook · 每周三、周六更新</div>
  <h1>Nook AI 雷达</h1>
  <p>追踪模型、Agent、数据与金融、医疗落地的关键动态。</p>
  <div class="meta"><span>共 <b class="num">{{COUNT}}</b> 期</span><span>最近更新 <span class="num">{{UPDATED}}</span></span></div>
</header>
{{ISSUES}}
<footer>源文件在 <a href="https://github.com/lyteboat/nook">GitHub · lyteboat/nook</a>。</footer>
</div>
{{NAV_JS}}</body>
</html>
"""


def main():
    issues = collect()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("")
    (OUT / "index.html").write_text(render_index(issues), encoding="utf-8")
    for n, i in enumerate(issues):
        dest = OUT / "radar" / i["rel"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(wrap_page(issues, n), encoding="utf-8")
    print(f"站点已生成：{OUT}，共 {len(issues)} 期雷达")


if __name__ == "__main__":
    main()
