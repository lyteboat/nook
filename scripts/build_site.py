#!/usr/bin/env python3
"""生成 GitHub Pages 站点：雷达和随笔两个模块，墨红报刊版式。

扫描 radar/YYYY/YYYY-MM-DD.html、topics/YYYY/YYYY-MM-DD-slug.html、notes/YYYY/YYYY-MM-DD-slug.html。
- 首页（index.html）：最新一期的标题、一句话结论，本期专题，本期速览（技术、产品两栏，按总分排，必看四条标“必看”），最新随笔。
- 每期页面（radar/…）：雷达原文，补上站点的报头、菜单、页尾和上一期、下一期翻页。
- 专题（topics.html、topics/…）：长文解读，封面的 data-after 写它接在哪一期之后，那一期在首页挂出它；
  专题页的 nook:related 标记处按封面的 data-tags 列出雷达里的相关条目。
- 全部条目（items.html）：汇总每期附录 A 的条目总表，可搜索，可按轨道、行业、阶段、标签筛选。
- 往期（archive.html）：每期的日期、标题、一句话结论和专题，点进每期页面。
- 随笔（notes.html、notes/…）：Yue 自己写的札记、长文、复盘、过招，按日期倒序。
旧的往期简报地址 brief/YYYY-MM-DD.html 改成跳转到每期页面。
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
TOPICS = ROOT / "topics"
NOTES = ROOT / "notes"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "_site")

WEEKDAYS = "一二三四五六日"
NAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.html$")
SLUG_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-([a-z0-9-]+)\.html$")
NOTE_KINDS = ["札记", "长文", "复盘", "过招"]
HEAD = (
    '<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
)
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;600;700;900'
    '&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;500;600&display=swap">\n'
)
STAGES = [("zs", "招熟", "上手即用", "招式练熟，拿来就能用"),
          ("dj", "懂劲", "原理机制", "懂得劲从哪里来、往哪里去"),
          ("sm", "神明", "长期方向", "不拘于招，也不拘于劲")]

# 站点外壳：报头、菜单、页尾、翻页。类名和变量都带 nk 前缀，套在雷达和专题页上时不和页面自己的样式冲突。
SHELL_CSS = """<style>
:root{--nk-bg:#F6F3EC;--nk-paper:#FCFAF5;--nk-ink:#1B1814;--nk-ink2:#3A342D;--nk-muted:#6E665C;--nk-line:#DDD5C8;--nk-rule:#1B1814;
--nk-accent:#A12F2B;--nk-on-accent:#fff;--nk-soft:#EFE9DE;--nk-zs:#2f7d5b;--nk-dj:#3d55a3;--nk-sm:#a1701c;
--nk-display:"Noto Serif SC","Songti SC","STSong",serif;--nk-body:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;
--nk-data:"JetBrains Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;--nk-gut:clamp(16px,3.2vw,56px)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--nk-bg:#15120F;--nk-paper:#1C1814;--nk-ink:#EDE6DA;--nk-ink2:#CFC6B8;--nk-muted:#A0968A;
--nk-line:#342D25;--nk-rule:#EDE6DA;--nk-accent:#E27D6E;--nk-on-accent:#1B1814;--nk-soft:#211C17;--nk-zs:#6cc59a;--nk-dj:#9aaef0;--nk-sm:#e0b45e;color-scheme:dark}}
:root[data-theme="dark"]{--nk-bg:#15120F;--nk-paper:#1C1814;--nk-ink:#EDE6DA;--nk-ink2:#CFC6B8;--nk-muted:#A0968A;
--nk-line:#342D25;--nk-rule:#EDE6DA;--nk-accent:#E27D6E;--nk-on-accent:#1B1814;--nk-soft:#211C17;--nk-zs:#6cc59a;--nk-dj:#9aaef0;--nk-sm:#e0b45e;color-scheme:dark}
.nk-w{max-width:1600px;margin:0 auto;padding:0 var(--nk-gut);box-sizing:border-box}
.nk-mast,.nk-nav,.nk-foot,.nk-pager{font-family:var(--nk-body);color:var(--nk-ink)}
.nk-mast a,.nk-nav a,.nk-foot a,.nk-pager a{color:inherit;text-decoration:none}
.nk-mh{display:grid;grid-template-columns:1fr auto 1fr;align-items:end;gap:24px;padding-top:28px;padding-bottom:14px}
.nk-ml{font:500 12px/1.5 var(--nk-data);color:var(--nk-muted);letter-spacing:.04em;padding-bottom:6px}
.nk-logo{text-align:center}.nk-logo b{display:block;font:900 68px/.9 var(--nk-display);letter-spacing:.14em;margin-right:-.14em}
.nk-logo span{display:block;font:500 12px/1 var(--nk-display);letter-spacing:.42em;margin-right:-.42em;color:var(--nk-muted);margin-top:12px}
.nk-lvr{display:grid;justify-items:end;gap:3px;padding-bottom:2px}
.nk-lvr a,.nk-foot .nk-lv a{display:inline-flex;align-items:baseline;gap:8px;font:500 11.5px/1.5 var(--nk-body);color:var(--nk-muted)}
.nk-lvr b,.nk-lv b{font:700 12.5px/1.5 var(--nk-display);color:var(--c)}
.nk-lvr a::before,.nk-lv a::before{content:"";width:5px;height:5px;border-radius:50%;background:var(--c);align-self:center}
.nk-zs{--c:var(--nk-zs)}.nk-dj{--c:var(--nk-dj)}.nk-sm{--c:var(--nk-sm)}
.nk-rule2{border:0;border-top:1px solid var(--nk-rule);box-shadow:0 3px 0 -2px var(--nk-rule);height:4px;margin:0}
.nk-bar{display:flex;justify-content:center;align-items:center;gap:36px;height:50px;border-bottom:1px solid var(--nk-rule)}
.nk-bar a{font:600 15px/1 var(--nk-display);color:var(--nk-ink2);padding:6px 0;border-bottom:2px solid transparent;white-space:nowrap}
.nk-bar a[aria-current]{color:var(--nk-accent);border-bottom-color:var(--nk-accent)}.nk-bar a:hover{color:var(--nk-accent)}
.nk-bar .sep{width:1px;height:16px;background:var(--nk-line)}
.nk-mini .nk-mh{display:flex;align-items:center;justify-content:space-between;gap:24px;padding-top:16px;padding-bottom:12px}
.nk-mini .nk-logo{display:flex;align-items:baseline;gap:14px;text-align:left}
.nk-mini .nk-logo b{font-size:28px;letter-spacing:.12em;margin:0}.nk-mini .nk-logo span{margin:0;letter-spacing:.3em}
.nk-mini .nk-bar{height:auto;border:0;gap:28px}
.nk-foot{margin-top:72px}.nk-foot .nk-w>div{border-top:1px solid var(--nk-line);padding:20px 0 40px;display:flex;flex-wrap:wrap;gap:8px 32px;justify-content:space-between;font-size:12.5px;color:var(--nk-muted)}
.nk-foot .nk-lv{display:flex;flex-wrap:wrap;gap:4px 18px}.nk-foot a:hover{color:var(--nk-accent)}
.nk-pager{max-width:880px;margin:56px auto 0;padding:0 16px;display:grid;grid-template-columns:1fr 1fr;gap:16px;box-sizing:border-box}
.nk-pager a{display:grid;gap:4px;padding:14px 0;border-top:1px solid var(--nk-rule);font:600 15px/1.5 var(--nk-display)}
.nk-pager a:hover{color:var(--nk-accent)}.nk-pager .next{grid-column:2;text-align:right}
.nk-pager small{font:500 12px/1.4 var(--nk-data);color:var(--nk-muted)}
:focus-visible{outline:2px solid var(--nk-accent);outline-offset:3px;border-radius:2px}
@media (max-width:760px){.nk-mh{grid-template-columns:1fr;padding-top:20px;justify-items:center}.nk-ml{display:none}
.nk-logo b{font-size:44px}.nk-logo span{font-size:11px;margin-top:8px}
.nk-lvr{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 16px}.nk-lvr a span{display:none}
.nk-bar{justify-content:flex-start;gap:24px;overflow-x:auto;scrollbar-width:none}.nk-bar>*{flex:none}
.nk-mini .nk-mh{flex-direction:column;align-items:flex-start;gap:8px}.nk-mini .nk-bar{width:100%}
.nk-pager{grid-template-columns:1fr}.nk-pager .next{grid-column:1;text-align:left}}
main .nk-pager{padding:0}
</style>
"""

# 首页、专题列表、全部条目、往期、随笔这些站点自己的页面
PAGE_CSS = """<style>
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--nk-bg);color:var(--nk-ink);font:15px/1.75 var(--nk-body);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}h1,h2,h3,h4,p,ol,ul{margin:0;padding:0}ol,ul{list-style:none}
h1,h2,h3,h4{font-family:var(--nk-display);word-break:keep-all;overflow-wrap:anywhere}p{text-wrap:pretty}
.num{font-family:var(--nk-data);font-variant-numeric:tabular-nums}
.kick{display:block;font:600 11px/1 var(--nk-data);letter-spacing:.16em;color:var(--nk-accent);margin-bottom:20px}
.dot{width:7px;height:7px;border-radius:50%;flex:none;background:var(--c)}
.zs{--c:var(--nk-zs)}.dj{--c:var(--nk-dj)}.sm{--c:var(--nk-sm)}
.stg{display:inline-flex;align-items:center;gap:5px;font:500 11.5px/1 var(--nk-body);color:var(--c);white-space:nowrap}
.stg::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--c)}
.tag{font:500 11px/1 var(--nk-body);color:var(--nk-muted);border:1px solid var(--nk-line);border-radius:3px;padding:3px 5px 2px;white-space:nowrap}
a.tag:hover{color:var(--nk-accent);border-color:var(--nk-accent)}
.must{font:700 10.5px/1 var(--nk-body);color:var(--nk-on-accent);background:var(--nk-accent);border-radius:3px;padding:3px 5px 2px;white-space:nowrap}
.empty{color:var(--nk-muted);padding:16px 0}
.sec{margin-top:56px}
.sec-h{display:flex;align-items:baseline;flex-wrap:wrap;gap:4px 16px;border-top:3px solid var(--nk-rule);padding-top:14px;margin-bottom:24px}
.sec-h h2{font-size:26px;line-height:1.2;font-weight:900}.sec-h p{font-size:13.5px;color:var(--nk-muted)}
.ph{padding:40px 0 8px}.ph h1{font-size:clamp(28px,1vw + 22px,40px);font-weight:900;line-height:1.25}.ph p{margin-top:10px;font-size:14px;color:var(--nk-muted)}
/* 首页 */
.lead{padding:40px 0 36px;border-bottom:1px solid var(--nk-line)}
.lead h1{text-wrap:pretty;font-size:clamp(29px,1.6vw + 22px,56px);line-height:1.25;font-weight:900;margin:0 0 20px}
.lead .dek{font:500 clamp(16px,.3vw + 14px,19px)/1.85 var(--nk-display);color:var(--nk-ink2)}
.lead a:hover h1{color:var(--nk-accent)}
.byl{display:flex;gap:16px;align-items:center;margin-top:22px;font-size:13px;color:var(--nk-muted)}.byl i{width:1px;height:12px;background:var(--nk-line)}
.byl a{color:var(--nk-accent);font-weight:500}
.tps{padding:28px 0 32px;border-bottom:1px solid var(--nk-line)}
.tps .two{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:24px 40px}
.feat{display:grid;grid-template-columns:40px 1fr;column-gap:12px;align-content:start}
.feat .no{font:900 30px/1 var(--nk-display);color:var(--nk-accent);padding-top:3px}
.feat h3{font-size:18px;line-height:1.5;font-weight:900}.feat:hover h3{color:var(--nk-accent)}
.feat p{grid-column:2;margin-top:8px;font-size:13.5px;line-height:1.75;color:var(--nk-muted)}
.feat .tags{grid-column:2;display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.brief{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:32px 48px}
.brief h3{font:600 11px/1 var(--nk-data);letter-spacing:.16em;color:var(--nk-muted);padding-bottom:12px;border-bottom:1px solid var(--nk-rule)}
.row{display:grid;grid-template-columns:7px 1fr auto;align-items:center;column-gap:12px;min-height:44px;padding:9px 0;border-bottom:1px dotted var(--nk-line);font-size:14.5px;line-height:1.55}
.row:hover .t{color:var(--nk-accent)}.row .meta{display:flex;gap:6px}
.elist li a{display:grid;grid-template-columns:5.5em 4em 1fr auto;align-items:baseline;gap:16px;padding:12px 0;border-bottom:1px dotted var(--nk-line);font-size:15px}
.elist .d{font-size:12.5px;color:var(--nk-muted)}.elist .k{font:600 12px var(--nk-body);color:var(--nk-accent);letter-spacing:.08em}
.elist .t{font-family:var(--nk-display);font-weight:600;color:var(--nk-ink2)}.elist a:hover .t{color:var(--nk-accent)}.elist .go{color:var(--nk-muted)}
.yr{font:600 12px/1 var(--nk-data);letter-spacing:.12em;color:var(--nk-muted);padding:28px 0 10px;border-bottom:1px solid var(--nk-rule)}
/* 专题列表、往期 */
.tlist>a,.alist>a{display:grid;grid-template-columns:9em minmax(0,1fr);column-gap:32px;padding:24px 0;border-bottom:1px solid var(--nk-line)}
.tlist .d,.alist .d{font:500 12.5px/1.9 var(--nk-data);color:var(--nk-muted)}
.tlist h2,.alist h2{font-size:21px;line-height:1.45;font-weight:900}.tlist a:hover h2,.alist a:hover h2{color:var(--nk-accent)}
.tlist p,.alist p{margin-top:8px;font:500 14.5px/1.85 var(--nk-display);color:var(--nk-ink2);max-width:52em}
.tlist .tags,.alist .tags{display:flex;flex-wrap:wrap;gap:6px 10px;margin-top:12px;font-size:13px;color:var(--nk-muted)}
.alist .tp b{color:var(--nk-accent);font-weight:600;margin-right:6px}
/* 全部条目 */
.filters{display:grid;gap:10px;position:sticky;top:0;z-index:5;background:var(--nk-bg);padding:14px 0;border-bottom:1px solid var(--nk-rule)}
.filters input{width:100%;font:inherit;padding:9px 14px;border:1px solid var(--nk-line);border-radius:4px;background:var(--nk-paper);color:var(--nk-ink)}
.fr{display:flex;gap:8px;flex-wrap:wrap;align-items:center;font-size:13px}.fr .lab{color:var(--nk-muted);width:3em;flex:none}
.f{font:inherit;font-size:13px;border:1px solid var(--nk-line);background:var(--nk-paper);color:var(--nk-ink2);border-radius:999px;padding:2px 12px;cursor:pointer}
.f[aria-pressed="true"]{background:var(--nk-ink);color:var(--nk-bg);border-color:var(--nk-ink)}.f .num{font-size:11px;opacity:.6;margin-left:2px}
.count{font-size:13px;color:var(--nk-muted);margin-left:auto}
.ilist li{display:grid;grid-template-columns:4.5em 7px minmax(0,1fr) auto;column-gap:14px;align-items:baseline;padding:14px 0;border-bottom:1px dotted var(--nk-line)}
.ilist .d{font:500 12.5px var(--nk-data);color:var(--nk-muted)}.ilist .dot{align-self:center}
.ilist .t{font-weight:600;font-size:15px}.ilist .t a:hover{color:var(--nk-accent)}
.ilist .so{display:block;font-size:13.5px;color:var(--nk-muted);margin-top:2px}
.ilist .meta{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end;align-items:center}
.ilist .iss{font:500 12px var(--nk-data);color:var(--nk-muted)}.ilist .iss:hover{color:var(--nk-accent)}
/* 随笔正文 */
.note{max-width:720px;margin:0 auto;padding:40px 0 0}
.note .ek{display:flex;gap:12px;font:600 12px/1 var(--nk-data);letter-spacing:.08em;color:var(--nk-muted)}.note .ek b{color:var(--nk-accent)}
.note h1{font-size:clamp(28px,1vw + 22px,40px);line-height:1.3;font-weight:900;margin:16px 0 28px}
.note .body{font:400 17px/2 var(--nk-display);color:var(--nk-ink2)}
.note .body>*+*{margin-top:1.1em}.note .body h2{font-size:21px;font-weight:900;color:var(--nk-ink);margin-top:2em}
.note .body ul,.note .body ol{padding-left:1.4em}.note .body ul{list-style:disc}.note .body ol{list-style:decimal}
.note .body a{color:var(--nk-accent);text-decoration:underline;text-underline-offset:3px}
.note .body blockquote{margin:0;padding-left:16px;border-left:3px solid var(--nk-accent);color:var(--nk-muted)}
.note .ref{margin-top:40px;padding-top:14px;border-top:1px solid var(--nk-line);font-size:13.5px;color:var(--nk-muted)}.note .ref a{color:var(--nk-accent)}
@media (max-width:760px){.lead{padding:28px 0}.lead h1{font-size:29px;line-height:1.3;margin-bottom:14px}.lead .dek{font-size:16px;line-height:1.8}
.sec{margin-top:40px}.sec-h h2{font-size:22px}.sec-h p{flex-basis:100%}
.row{font-size:14px}.row .meta .tag{display:none}
.elist li a{grid-template-columns:3.4em 1fr;gap:4px 12px}.elist .k{grid-column:1;grid-row:2}.elist .t{grid-column:2;grid-row:1/3}.elist .go{display:none}
.tlist>a,.alist>a{grid-template-columns:1fr;row-gap:6px}
.filters{position:static}.fr.tg{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}.fr.tg>*{flex:none}.ilist li{grid-template-columns:7px minmax(0,1fr);row-gap:6px}.ilist .d{display:none}.ilist .meta{grid-column:2;justify-content:flex-start}}
</style>
"""

# 雷达和专题页自带一套主题，发布时换成站点的纸色、墨色和墨红，三阶段的颜色不动。
# 附录 A 是站点的数据源，“全部条目”页已经汇总，不在页面上再列一遍；条目的短名只给附录和数据对表用。
ISSUE_THEME = """<style>
:root{--bg:#F6F3EC;--surface:#FCFAF5;--ink:#1B1814;--muted:#6E665C;--line:#DDD5C8;--wash:#EFE9DE;--accent:#A12F2B;--prod:#6B4A86;
--cover:#211C17;--cover-ink:#EDE6DA;--cover-ink2:#A0968A}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15120F;--surface:#1C1814;--ink:#EDE6DA;--muted:#A0968A;--line:#342D25;--wash:#211C17;
--accent:#E27D6E;--prod:#C9A6E0;--cover:#0F0D0B;--cover-ink:#EDE6DA;--cover-ink2:#A0968A}}
:root[data-theme="dark"]{--bg:#15120F;--surface:#1C1814;--ink:#EDE6DA;--muted:#A0968A;--line:#342D25;--wash:#211C17;
--accent:#E27D6E;--prod:#C9A6E0;--cover:#0F0D0B;--cover-ink:#EDE6DA;--cover-ink2:#A0968A}
body{padding-left:0!important;padding-right:0!important}
.wrap{padding-left:16px;padding-right:16px}
.wrap h1,.wrap h2,.wrap h3{word-break:keep-all;overflow-wrap:anywhere}
[id^="i-"]{scroll-margin-top:24px}
[id^="i-"]:target{box-shadow:0 0 0 3px var(--accent)}
section[aria-labelledby="s-appx"],.must .item-meta .name{display:none}
</style>
"""


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def first(pattern, source):
    m = re.search(pattern, source, re.S)
    return text_of(m.group(1)) if m else ""


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
            "digest": digest(source),
            "source": source,
        })
    issues.sort(key=lambda i: i["date"], reverse=True)
    for n, i in enumerate(reversed(issues), 1):
        i["no"] = n
    return issues


def collect_topics():
    topics = []
    for path in sorted(TOPICS.glob("*/*.html")):
        m = SLUG_RE.match(path.name)
        if not m:
            continue
        source = path.read_text(encoding="utf-8")
        cover = re.search(r'<header class="cover[^"]*"([^>]*)>', source)
        attrs = dict(re.findall(r'data-(\w+)="([^"]*)"', cover.group(1))) if cover else {}
        topics.append({
            "date": datetime.date(*map(int, m.groups()[:3])),
            "rel": path.relative_to(TOPICS).as_posix(),
            "title": first(r"<h1[^>]*>(.*?)</h1>", source) or path.stem,
            "no": first(r"专题 (\d+)", source),
            "thesis": first(r'<p class="thesis">(.*?)</p>', source),
            "tags": [t for t in re.split(r"[、,，]\s*", attrs.get("tags", "")) if t],
            "after": attrs.get("after", ""),
            "source": source,
        })
    topics.sort(key=lambda t: t["no"])
    topics.sort(key=lambda t: t["date"], reverse=True)
    return topics


def collect_notes():
    """随笔是片段：<title>，加一个 <article class="note" data-kind="札记"> 包着 h1 和正文；data-ref 可写引用的那一期日期。"""
    notes = []
    for path in sorted(NOTES.glob("*/*.html")):
        m = SLUG_RE.match(path.name)
        if not m:
            continue
        source = path.read_text(encoding="utf-8")
        art = re.search(r'<article class="note"([^>]*)>(.*?)</article>', source, re.S)
        if not art:
            continue
        attrs = dict(re.findall(r'data-(\w+)="([^"]*)"', art.group(1)))
        inner = art.group(2)
        kind = attrs.get("kind", "")
        notes.append({
            "date": datetime.date(*map(int, m.groups()[:3])),
            "rel": path.relative_to(NOTES).as_posix(),
            "title": first(r"<h1[^>]*>(.*?)</h1>", inner) or path.stem,
            "kind": kind if kind in NOTE_KINDS else "札记",
            "ref": attrs.get("ref", ""),
            "body": re.sub(r"<h1[^>]*>.*?</h1>", "", inner, count=1, flags=re.S).strip(),
        })
    notes.sort(key=lambda n: n["date"], reverse=True)
    return notes


def attach_topics(issues, topics):
    """每期挂上接在它之后的专题，按专题编号排。"""
    for i in issues:
        i["topics"] = sorted((t for t in topics if t["after"] == str(i["date"])), key=lambda t: t["no"])


def by_year(rows):
    groups = {}
    for r in rows:
        groups.setdefault(r["date"].year, []).append(r)
    return groups


def digest(source):
    """从一期雷达里取站点要用的结构化内容：一句话结论、本期必看、附录 A 的条目总表。

    雷达按模板写，这些块都有固定的 class；某一期缺了哪块，就跳过哪块。
    """
    thesis = first(r'<p class="thesis">(.*?)</p>', source)
    # 每个条目是标题“主体｜做了什么”、副标题写意义，再加六栏。必看是展开的 article，其余条目是折叠的 details。
    musts = []
    for aid, art in re.findall(r'<article class="must[^"]*" id="([^"]+)"[^>]*>(.*?)</article>', source, re.S):
        musts.append({
            "anchor": "#" + aid, "title": first(r"<h3>(.*?)</h3>", art), "so": first(r'<p class="so">(.*?)</p>', art),
            "label": first(r'<span class="must-no">(.*?)</span>', art),
            "name": re.sub(r"^新\s*·\s*", "", first(r'<span class="name">(.*?)</span>', art)),
        })
    heads = {aid: (text_of(c), text_of(so)) for aid, c, so in re.findall(
        r'<details class="item" id="([^"]+)"[^>]*>\s*<summary><span class="c">(.*?)</span>(?:<span class="so">(.*?)</span>)?', source, re.S)}
    heads.update({m["anchor"][1:]: (m["title"], m["so"]) for m in musts})
    # 两条条目可能共用一个正文锚点（比如 Skills 和 OpenShell 写在同一段），所以必看先按短名对，对不上再按锚点
    items = []
    tbl = re.search(r"条目总表.*?<thead>(.*?)</thead>.*?<tbody>(.*?)</tbody>", source, re.S)
    cols = [text_of(th) for th in re.findall(r"<th[^>]*>(.*?)</th>", tbl.group(1), re.S)] if tbl else []
    for tr in re.findall(r"<tr>(.*?)</tr>", tbl.group(2) if tbl else "", re.S):
        row = dict(zip(cols, re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)))
        if "条目" not in row:
            continue
        chip = re.search(r"chip (zs|dj|sm)", row.get("阶段", ""))
        name = re.sub(r"^新\s*·\s*", "", text_of(row["条目"]))
        anchor = re.search(r'href="(#[^"]+)"', row["条目"])
        anchor = anchor.group(1) if anchor else ""
        # 早期的表头叫“方向”，还有一类“产品”，现在统一归到行业的“通用”。
        industry = text_of(row.get("行业", row.get("方向", ""))) or "通用"
        title, so = heads.get(anchor[1:], ("", ""))
        items.append({
            "date": text_of(row.get("日期", "")), "ind": industry if industry in INDUSTRIES else "通用",
            "cls": chip.group(1) if chip else "", "stage": text_of(row.get("阶段", "")),
            "name": name, "title": title or name, "so": so,
            "tags": [t for t in re.split(r"[、,，/]\s*", text_of(row.get("标签", ""))) if t],
            "src": text_of(row.get("来源", "")), "anchor": anchor,
            # 轨道和总分从 10-24 那期起才有，更早的期数留空
            "track": text_of(row.get("轨道", "")), "score": int(text_of(row.get("总分", "")) or 0),
        })
    names = {x["name"] for x in items}
    for m in musts:
        hit = [x for x in items if x["name"] == m["name"]] if m["name"] in names else [x for x in items if x["anchor"] == m["anchor"]]
        for x in hit[:1]:
            x["must"], x["title"], x["so"] = m["label"], m["title"], m["so"]
    return {"thesis": thesis, "musts": musts, "items": items}


INDUSTRIES = ["通用", "金融", "医疗"]
TRACKS = ["技术", "产品"]
CURRENT = ' aria-current="page"'


def esc(s):
    return html.escape(s)


def cn_date(d):
    return f"{d.year} 年 {d.month} 月 {d.day} 日 星期{WEEKDAYS[d.weekday()]}"


def stage_links(prefix):
    return "".join(f'<a class="nk-{c}" href="{prefix}items.html#stage={quote(n)}" title="{n}：{tip}"><b>{n}</b><span>{short}</span></a>'
                   for c, n, short, tip in STAGES)


def nav(current, prefix):
    home = prefix or "./"
    links = [("home", home, "本期"), ("topics", prefix + "topics.html", "专题"), ("items", prefix + "items.html", "全部条目"),
             ("archive", prefix + "archive.html", "往期")]
    out = "".join(f'<a href="{h}"{CURRENT if k == current else ""}>{label}</a>' for k, h, label in links)
    return out + f'<span class="sep" aria-hidden="true"></span><a href="{prefix}notes.html"{CURRENT if current == "notes" else ""}>随笔</a>'


def header(current, prefix, issue=None):
    """首页是完整报头；其余页面是一行的小报头，三阶段说明移到页尾。"""
    home = prefix or "./"
    if issue:
        return (f'<header class="nk-mast"><div class="nk-w nk-mh"><div class="nk-ml">第 {issue["no"]} 期 · {cn_date(issue["date"])}</div>'
                f'<a class="nk-logo" href="{home}"><b>NOOK</b><span>一个思考 AI 的角落</span></a>'
                f'<div class="nk-lvr" aria-label="阅读阶段">{stage_links(prefix)}</div></div>'
                f'<div class="nk-w"><hr class="nk-rule2"></div></header>\n'
                f'<nav class="nk-nav" aria-label="栏目"><div class="nk-w"><div class="nk-bar">{nav(current, prefix)}</div></div></nav>\n')
    return (f'<header class="nk-mast nk-mini"><div class="nk-w nk-mh"><a class="nk-logo" href="{home}"><b>NOOK</b><span>一个思考 AI 的角落</span></a>'
            f'<nav class="nk-bar" aria-label="栏目">{nav(current, prefix)}</nav></div><div class="nk-w"><hr class="nk-rule2"></div></header>\n')


def footer(prefix, with_stages=True):
    lv = f'<div class="nk-lv">{stage_links(prefix)}</div>' if with_stages else ""
    return (f'<footer class="nk-foot"><div class="nk-w"><div>{lv}<span>雷达每周三、周六出刊 · 随笔不定期 · 源文件在 '
            '<a href="https://github.com/lyteboat/nook">GitHub：lyteboat/nook</a></span></div></div></footer>\n')


def page(title, desc, current, body, script="", prefix="", issue=None):
    """prefix 是从当前页面回到站点根目录的相对路径。issue 只在首页传，用来出完整报头。"""
    return (HEAD + f"<title>{esc(title)}</title>\n<meta name=\"description\" content=\"{esc(desc)}\">\n{FONTS}{SHELL_CSS}{PAGE_CSS}</head>\n<body>\n"
            + header(current, prefix, issue) + f'<main class="nk-w">\n{body}\n</main>\n' + footer(prefix, issue is None)
            + f"{script}</body>\n</html>\n")


def pager(prev, nxt, unit="期"):
    """prev 是更早的一篇，nxt 是更新的一篇，各是（链接，日期，标题）。"""
    links = []
    if prev:
        links.append(f'<a href="{prev[0]}"><small>← 上一{unit} {prev[1]}</small>{esc(prev[2])}</a>')
    if nxt:
        links.append(f'<a class="next" href="{nxt[0]}"><small>下一{unit} {nxt[1]} →</small>{esc(nxt[2])}</a>')
    return f'<nav class="nk-pager" aria-label="翻页">{"".join(links)}</nav>\n' if links else ""


def wrap_fragment(source, current, extra="", tail=""):
    """雷达和专题是不带 <html>/<head> 的片段：补上骨架，在样式之后插入站点主题和报头，末尾加翻页和页尾。"""
    cut = source.rfind("</style>")
    cut = cut + len("</style>") if cut != -1 else 0
    return (HEAD + source[:cut] + "\n" + ISSUE_THEME + SHELL_CSS + extra + header(current, "../../")
            + source[cut:] + "\n" + tail + footer("../../") + "</html>\n")


def wrap_issue(issues, n):
    issue = issues[n]
    titles = {x["anchor"]: x["title"] for x in issue["digest"]["items"]}
    # 本期行动里的链接原来写附录的短名，换成条目标题，一个条目在页面上只有一个名字
    source = re.sub(r'(<ol class="acts">.*?</ol>)', lambda m: re.sub(
        r'<a href="(#[^"]+)">.*?</a>', lambda a: f'<a href="{a.group(1)}">{esc(titles.get(a.group(1), text_of(a.group(0))))}</a>', m.group(1)),
        issue["source"], flags=re.S)
    prev = issues[n + 1] if n + 1 < len(issues) else None
    nxt = issues[n - 1] if n > 0 else None
    tail = pager(prev and (f'../../radar/{prev["rel"]}', prev["date"], prev["title"]),
                 nxt and (f'../../radar/{nxt["rel"]}', nxt["date"], nxt["title"]))
    return wrap_fragment(source, "home" if n == 0 else "archive", tail=tail)


def wrap_topic(issues, topic):
    """在 nook:related 标记处插入雷达里的相关条目。"""
    source = re.sub(r"<!-- nook:related.*?-->", lambda _: related_items(issues, topic), topic["source"], flags=re.S)
    return wrap_fragment(source, "topics")


def related_items(issues, topic):
    rows = []
    for i in issues:
        for x in i["digest"]["items"]:
            if any(t in topic["tags"] for t in x["tags"]):
                rows.append(f'<tr><td class="num">{esc(x["date"])}</td><td><a href="../../radar/{i["rel"]}{x["anchor"]}">'
                            f'{esc(x["title"])}</a></td><td>{"、".join(map(esc, x["tags"]))}</td></tr>')
    if not rows:
        return ""
    return ('<section aria-labelledby="t-rel"><h2 id="t-rel">雷达里的相关条目<span class="sub">按标签 '
            + "、".join(map(esc, topic["tags"])) + ' 自动汇总</span></h2><div class="tbl"><table><thead><tr><th>日期</th><th>条目</th>'
            '<th>标签</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div></section>')


def wrap_note(notes, n):
    note = notes[n]
    d = note["date"]
    ref = ""
    if note["ref"]:
        ref = f'<p class="ref">引自 <a href="../../radar/{note["ref"][:4]}/{esc(note["ref"])}.html">{note["ref"][5:]} 期雷达</a></p>'
    prev = notes[n + 1] if n + 1 < len(notes) else None
    nxt = notes[n - 1] if n > 0 else None
    body = (f'<article class="note"><div class="ek"><b>{note["kind"]}</b><span>{d} 周{WEEKDAYS[d.weekday()]}</span></div>'
            f'<h1>{esc(note["title"])}</h1><div class="body">{note["body"]}</div>{ref}</article>'
            + pager(prev and (f'../../notes/{prev["rel"]}', prev["date"], prev["title"]),
                    nxt and (f'../../notes/{nxt["rel"]}', nxt["date"], nxt["title"]), "篇"))
    return page(f'{note["title"]} · Nook 随笔', note["title"], "notes", body, prefix="../../")


def tag_list(tags, prefix=""):
    return "".join(f'<a class="tag" href="{prefix}items.html#tag={quote(t)}">{esc(t)}</a>' for t in tags)


def note_rows(notes, prefix=""):
    return "".join(f'<li><a href="{prefix}notes/{x["rel"]}"><span class="d num">{x["date"]:%m-%d}</span><span class="k">{x["kind"]}</span>'
                   f'<span class="t">{esc(x["title"])}</span><span class="go">→</span></a></li>' for x in notes)


def read_minutes(source):
    """按每分钟读 500 个字估算，附录不算。"""
    body = re.sub(r'<section aria-labelledby="s-appx">.*?</section>|<style.*?</style>|<!--.*?-->', "", source, flags=re.S)
    return max(1, round(len(text_of(body)) / 500))


def render_home(issues, topics, notes):
    if not issues:
        return page("Nook", "", "home", '<p class="empty">还没有雷达。</p>')
    latest = issues[0]
    dg = latest["digest"]
    href = f'radar/{latest["rel"]}'
    blocks = [f'<section class="lead"><a href="{href}"><h1>{esc(latest["title"])}</h1>'
              + (f'<p class="dek">{esc(dg["thesis"])}</p>' if dg["thesis"] else "")
              + f'</a><p class="byl"><span>{len(dg["items"])} 条</span><i></i><span>约 {read_minutes(latest["source"])} 分钟</span>'
              f'<a href="{href}">读全文 →</a></p></section>']
    shown = latest["topics"] or topics[:2]
    if shown:
        blocks.append('<section class="tps" aria-label="专题"><span class="kick">专题</span><div class="two">' + "".join(
            f'<a class="feat" href="topics/{t["rel"]}"><span class="no">{esc(t["no"])}</span><h3>{esc(t["title"])}</h3>'
            + (f'<p>{esc(t["thesis"])}</p>' if t["thesis"] else "")
            + f'<span class="tags">{"".join(f"<span class=tag>{esc(x)}</span>" for x in t["tags"])}</span></a>' for t in shown) + '</div></section>')
    if dg["items"]:
        cols = []
        for track in TRACKS:
            rows = sorted((x for x in dg["items"] if x["track"] == track), key=lambda x: (not x.get("must"), -x["score"]))
            if not rows:
                continue
            lis = "".join(f'<li><a class="row" href="{href}{x["anchor"]}"><span class="dot {x["cls"]}"></span><span class="t">{esc(x["title"])}</span>'
                          '<span class="meta">' + ('<span class="must">必看</span>' if x.get("must") else "")
                          + (f'<span class="tag">{x["ind"]}</span>' if x["ind"] != "通用" else "") + '</span></a></li>' for x in rows)
            cols.append(f'<div><h3>{track}</h3><ul>{lis}</ul></div>')
        blocks.append('<section class="sec" aria-labelledby="s-brief"><div class="sec-h"><h2 id="s-brief">本期速览</h2>'
                      f'<p>按重要程度排序，技术、产品各有两条必看</p></div><div class="brief">{"".join(cols)}</div></section>')
    if notes:
        blocks.append('<section class="sec" aria-labelledby="s-notes"><div class="sec-h"><h2 id="s-notes">随笔</h2><p>经验、复盘和零碎的想法</p></div>'
                      f'<ul class="elist">{note_rows(notes[:6])}</ul></section>')
    return page("Nook · 一个思考 AI 的角落", dg["thesis"] or latest["title"], "home", "\n".join(blocks), issue=latest)


def render_topics(topics):
    rows = "".join(f'<a href="topics/{t["rel"]}"><span class="d">专题 {esc(t["no"])} · {t["date"]:%m-%d}</span><div><h2>{esc(t["title"])}</h2>'
                   + (f'<p>{esc(t["thesis"])}</p>' if t["thesis"] else "")
                   + f'<span class="tags">{"".join(f"<span class=tag>{esc(x)}</span>" for x in t["tags"])}</span></div></a>' for t in topics)
    body = ('<section class="ph"><h1>专题</h1><p>雷达之外的长文：一个方向、一个行业或一种做法，按招熟、懂劲、神明展开</p></section>'
            + (f'<section class="tlist">{rows}</section>' if rows else '<p class="empty">还没有专题。</p>'))
    return page("专题 · Nook", "雷达之外的长文解读，按招熟、懂劲、神明三阶段展开。", "topics", body)


def render_archive(issues):
    parts = []
    for y, group in by_year(issues).items():
        parts.append(f'<div class="yr">{y}</div>')
        for i in group:
            d, dg = i["date"], i["digest"]
            tps = "".join(f'<span class="tp"><b>专题 {esc(t["no"])}</b>{esc(t["title"])}</span>' for t in i["topics"])
            parts.append(f'<a href="radar/{i["rel"]}"><span class="d">{d:%m-%d} 周{WEEKDAYS[d.weekday()]}<br>第 {i["no"]} 期 · {len(dg["items"])} 条</span>'
                         f'<div><h2>{esc(i["title"])}</h2>' + (f'<p>{esc(dg["thesis"])}</p>' if dg["thesis"] else "")
                         + (f'<span class="tags">{tps}</span>' if tps else "") + '</div></a>')
    body = '<section class="ph"><h1>往期</h1><p>每周三、周六各一期，点进去读全文</p></section>' + f'<section class="alist">{"".join(parts)}</section>'
    return page("往期 · Nook", "历期 AI 雷达的标题和一句话结论。", "archive", body)


def render_notes(notes):
    parts = "".join(f'<div class="yr">{y}</div><ul class="elist">{note_rows(group)}</ul>' for y, group in by_year(notes).items())
    body = ('<section class="ph"><h1>随笔</h1><p>经验、复盘和零碎的想法。写法分四种：札记、长文、复盘、过招</p></section>'
            + (parts or '<p class="empty">还没有随笔。</p>'))
    return page("随笔 · Nook", "Yue 的经验、复盘和零碎的想法。", "notes", body)


ITEMS_JS = """<script>
(function(){
  var D=JSON.parse(document.getElementById('data').textContent),sel={track:{},ind:{},stage:{},tag:{}};
  var ST={'招熟':'zs','懂劲':'dj','神明':'sm'};
  function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function ok(k,vs){var s=sel[k],any=false;vs=[].concat(vs);for(var x in s)if(s[x]){any=true;if(vs.indexOf(x)>-1)return true}return !any}
  function draw(){
    var q=document.getElementById('q').value.trim().toLowerCase();
    var rows=D.filter(function(i){return ok('track',i.track)&&ok('ind',i.ind)&&ok('stage',i.stage)&&ok('tag',i.tags)&&(!q||(i.title+' '+i.so+' '+i.name+' '+i.src+' '+i.tags.join(' ')).toLowerCase().indexOf(q)>-1)});
    document.getElementById('count').textContent='显示 '+rows.length+' / '+D.length+' 条';
    document.getElementById('tb').innerHTML=rows.map(function(i){return '<li><span class="d">'+e(i.date)+'</span><span class="dot '+i.cls+'" title="'+e(i.stage)+'"></span>'+
      '<span class="t"><a href="'+i.href+i.anchor+'">'+e(i.title)+'</a>'+(i.so?'<span class="so">'+e(i.so)+'</span>':'')+'</span><span class="meta">'+
      (i.must?'<span class="must">必看</span>':'')+(i.ind!=='通用'?'<span class="tag">'+e(i.ind)+'</span>':'')+
      i.tags.map(function(t){return '<a class="tag" href="#tag='+encodeURIComponent(t)+'">'+e(t)+'</a>'}).join('')+
      '<a class="iss" href="'+i.href+'">'+e(i.issue.slice(5))+' 期</a></span></li>'}).join('')||'<li class="empty">没有符合条件的条目。</li>';
  }
  [].forEach.call(document.querySelectorAll('.f'),function(b){b.addEventListener('click',function(){
    var on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',on);sel[b.dataset.k][b.dataset.v]=on;draw()})});
  function fromHash(){var m=/^#(tag|stage)=(.+)$/.exec(location.hash);if(!m)return;var k=m[1],t=decodeURIComponent(m[2]);sel[k]={};sel[k][t]=true;
    [].forEach.call(document.querySelectorAll('.f[data-k="'+k+'"]'),function(b){b.setAttribute('aria-pressed',b.dataset.v===t)})}
  window.addEventListener('hashchange',function(){fromHash();draw()});
  document.getElementById('q').addEventListener('input',draw);fromHash();draw();
})();
</script>
"""


def render_items(issues):
    items = []
    for i in issues:
        rows = sorted(i["digest"]["items"], key=lambda x: (not x.get("must"), -x["score"]))
        items += [dict(x, must=bool(x.get("must")), issue=str(i["date"]), href=f'radar/{i["rel"]}') for x in rows]
    counts = {}
    for x in items:
        for t in x["tags"]:
            counts[t] = counts.get(t, 0) + 1
    tags = sorted(counts, key=lambda t: (-counts[t], t))

    def chips(key, vals):
        return "".join(f'<button type="button" class="f" aria-pressed="false" data-k="{key}" data-v="{v}">{lab}</button>' for v, lab in vals)

    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    body = ('<section class="ph"><h1>全部条目</h1><p>历期雷达的全部条目，每期之内按重要程度排序；点标题读这一条的详情</p></section>'
            '<section><div class="filters">'
            '<input id="q" type="search" placeholder="搜索标题、标签或来源，比如 RAG、FSB、medRxiv" aria-label="搜索">'
            f'<div class="fr"><span class="lab">轨道</span>{chips("track", [(x, x) for x in TRACKS])}'
            f'<span class="lab" style="margin-left:16px">行业</span>{chips("ind", [(x, x) for x in INDUSTRIES])}'
            f'<span class="lab" style="margin-left:16px">阶段</span>{chips("stage", [(s[1], s[1]) for s in STAGES])}'
            '<span class="count" id="count"></span></div>'
            f'<div class="fr tg"><span class="lab">标签</span>{chips("tag", [(t, f"{esc(t)}<span class=num>{counts[t]}</span>") for t in tags])}</div></div>'
            '<ul class="ilist" id="tb"></ul></section>\n'
            f'<script type="application/json" id="data">{data}</script>')
    return page("全部条目 · Nook", "历期 AI 雷达的全部条目，可按轨道、行业、阶段、标签筛选。", "items", body, ITEMS_JS)


def redirect(target):
    return (HEAD + f'<meta http-equiv="refresh" content="0; url={target}">\n<link rel="canonical" href="{target}">\n'
            f'<title>Nook</title>\n</head>\n<body><a href="{target}">这一期已移到这里</a></body>\n</html>\n')


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    issues = collect()
    topics = collect_topics()
    notes = collect_notes()
    attach_topics(issues, topics)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("")
    write(OUT / "index.html", render_home(issues, topics, notes))
    write(OUT / "items.html", render_items(issues))
    write(OUT / "archive.html", render_archive(issues))
    write(OUT / "topics.html", render_topics(topics))
    write(OUT / "notes.html", render_notes(notes))
    for n, i in enumerate(issues):
        write(OUT / "radar" / i["rel"], wrap_issue(issues, n))
        write(OUT / "brief" / f'{i["date"]}.html', redirect(f'../radar/{i["rel"]}'))
    for t in topics:
        write(OUT / "topics" / t["rel"], wrap_topic(issues, t))
    for n, x in enumerate(notes):
        write(OUT / "notes" / x["rel"], wrap_note(notes, n))
    print(f"站点已生成：{OUT}，共 {len(issues)} 期雷达、{len(topics)} 篇专题、{len(notes)} 篇随笔")


if __name__ == "__main__":
    main()
