# Nook

> 磨刀不误砍柴工。一个安静的角落，用来沉淀我在 AI 领域的学习与思考。

Nook 是一本持续生长的书：**《Nook：我的 AI 指南针》**。它由两路输入喂养——我的问题与思考、外部 AI 世界的最新动态——经过讨论和提炼，最终归档进有首页、有目录、有章节的书稿里。

书稿用 Markdown 写作，用 [mdBook](https://rust-lang.github.io/mdBook/) 生成网站，以后也可以导出 PDF 或整理出版。

在线阅读：<https://lyteboat.github.io/nook/>。每次合并到 main，GitHub Actions 自动构建并发布到 GitHub Pages。

## 目录结构

```text
nook/
├── src/                 正式书稿（mdBook 源文件）
│   ├── README.md        首页
│   ├── SUMMARY.md       全书目录（mdBook 依据它生成侧边栏）
│   ├── preface.md       前言
│   ├── part1-…/         各篇，一篇一个目录，一章一个文件
│   └── appendix/        附录：术语表、信息源清单、版本记录
├── drafts/              草稿池（临时，定期清理）
│   ├── inbox/           新进来的想法、问题、讨论片段
│   ├── _template.md     草稿模板
│   └── _template-study.html  讨论草稿模板（HTML，招熟、懂劲、神明）
├── radar/               外部动态雷达存档（长期保留）
│   ├── 2026/            按年份归档，每周三、周六各一期
│   └── _template.html   雷达模板（HTML）
├── meta/                写作规范与维护流程
│   ├── backlog.md       待研究清单
│   ├── maintenance/     每周维护报告（HTML，每周日一份）
│   ├── learner.md       我的背景与学习法（招熟、懂劲、神明）
│   ├── roles.md         讨论角色与报告流程
│   ├── style-guide.md   写作规范
│   └── workflow.md      从输入到成书的流程、草稿清理规则
├── book.toml            mdBook 配置
└── CLAUDE.md            给 Claude 的仓库约定
```

| 目录 | 放什么 | 生命周期 |
| --- | --- | --- |
| `src/` | 已经想清楚、可以成为书的一部分的内容 | 永久，持续修订 |
| `drafts/` | 还没想清楚的问题、想法、讨论片段 | **临时**，归档或删除 |
| `radar/` | 每期外部动态雷达的原始记录 | 永久，作为参考素材 |
| `meta/` | 这本书本身怎么写、怎么维护 | 永久 |

## 知识的流转

```text
我的问题 / 想法 ──► drafts/inbox ──┐
                                   ├──► 讨论、提炼 ──► src/ 对应章节
外部动态 ──► radar/YYYY/ ──────────┘
```

1. **进入**：我的输入写成草稿放进 `drafts/inbox/`；外部动态每周三、周六各生成一期，存入 `radar/`。
2. **提炼**：雷达里值得入书的条目，经我确认后转成草稿或直接写进章节。
3. **归档**：草稿成熟后合并进 `src/` 对应章节，原草稿删除（Git 历史里仍可追溯）。

## 草稿清理规则

草稿池是临时区，必须保持清爽：

- **每周六**随雷达一起做一次草稿盘点。
- 每份草稿只有三种去向：**归档**进章节、**保留**继续讨论、**删除**。
- 草稿创建超过 **30 天**仍未归档，盘点时必须做出决定：归档、删除，或写明保留理由并延期一次（最多延期一次）。
- 归档后删除原草稿，并在章节的“参考资料”里留下来源。

完整流程见 [meta/workflow.md](meta/workflow.md)。

## 本地预览

```bash
# 安装 mdBook：https://rust-lang.github.io/mdBook/guide/installation.html
mdbook serve --open
```

构建产物输出到 `book/`，已被 Git 忽略。
