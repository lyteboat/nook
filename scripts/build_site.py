#!/usr/bin/env python3
"""生成 GitHub Pages 站点：雷达首页 + 每期雷达。

扫描 radar/YYYY/YYYY-MM-DD.html，按日期倒序生成首页目录，
把每期雷达补上 doctype、charset、viewport 和返回首页的链接后复制到输出目录。
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
HEAD = (
    '<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
)
BACK = (
    '<nav style="max-width:880px;margin:20px auto 0;font-size:13px">'
    '<a href="../../" style="color:var(--accent,#1f5f58)">← 全部雷达</a></nav>\n'
)


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def first(pattern, source):
    m = re.search(pattern, source, re.S)
    return text_of(m.group(1)) if m else ""


def wrap_page(source):
    """雷达是不带 <html>/<head> 的片段：补上骨架，在样式之后插入返回链接。"""
    if re.match(r"\s*<!doctype", source, re.I):
        return source
    cut = source.rfind("</style>")
    if cut != -1:
        cut += len("</style>")
        source = source[:cut] + "\n" + BACK + source[cut:]
    return HEAD + source + "\n</html>\n"


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
            "eyebrow": first(r'class="eyebrow"[^>]*>(.*?)</', source),
            "source": source,
        })
    issues.sort(key=lambda i: i["date"], reverse=True)
    return issues


def render_index(issues):
    rows = []
    for n, i in enumerate(issues):
        d = i["date"]
        cls = "issue latest" if n == 0 else "issue"
        badge = '<span class="badge">最新</span>' if n == 0 else ""
        rows.append(
            f'<li class="{cls}"><a href="radar/{i["rel"]}">'
            f'<span class="date num">{d:%Y-%m-%d}<small>周{WEEKDAYS[d.weekday()]}</small></span>'
            f'<span class="title">{html.escape(i["title"])}{badge}</span></a></li>'
        )
    body = "\n".join(rows) if rows else '<li class="empty">还没有雷达。</li>'
    updated = issues[0]["date"].isoformat() if issues else "—"
    return INDEX.replace("{{ISSUES}}", body).replace("{{COUNT}}", str(len(issues))).replace("{{UPDATED}}", updated)


INDEX = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nook AI 雷达</title>
<meta name="description" content="每周三、周六各一期，追踪 AI 模型、Agent、数据与行业落地的关键动态。">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;900&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
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
</head>
<body>
<div class="wrap">
<header>
  <div class="eyebrow">Nook · 每周三、周六更新</div>
  <h1>Nook AI 雷达</h1>
  <p>追踪模型、Agent、数据与金融、医疗落地的关键动态。每期先讲 1 到 3 条必懂的信号，再按“招熟、懂劲、神明”三个阶段展开。</p>
  <div class="meta"><span>共 <b class="num">{{COUNT}}</b> 期</span><span>最近更新 <span class="num">{{UPDATED}}</span></span></div>
</header>
<ol>
{{ISSUES}}
</ol>
<footer>源文件在 <a href="https://github.com/lyteboat/nook">GitHub · lyteboat/nook</a>。书稿《Nook：我的 AI 指南针》仍在写作中，成稿后在这里上线。</footer>
</div>
</body>
</html>
"""


def main():
    issues = collect()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("")
    (OUT / "index.html").write_text(render_index(issues), encoding="utf-8")
    for i in issues:
        dest = OUT / "radar" / i["rel"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(wrap_page(i["source"]), encoding="utf-8")
    print(f"站点已生成：{OUT}，共 {len(issues)} 期雷达")


if __name__ == "__main__":
    main()
