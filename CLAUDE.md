# Nook 仓库约定

这是 Yue 的 AI 学习之书《Nook：我的 AI 指南针》，用 mdBook 构建，正文使用简体中文。

- 正式书稿在 `src/`，目录在 `src/SUMMARY.md`。新增或移动章节必须同步更新 `SUMMARY.md`，并在 `src/appendix/changelog.md` 记录。
- 未成形的内容放 `drafts/inbox/`，用 `drafts/_template.md`，文件名 `YYYY-MM-DD-主题.md`。不要把草稿直接写进 `src/`。
- 外部动态雷达放 `radar/YYYY/YYYY-MM-DD.html`，用 `radar/_template.html`，每周三、周六各一期。
- 每周维护报告放 `meta/maintenance/YYYY-MM-DD.html`，用 `meta/maintenance/_template.html`，每周日一份。
- 默认只产出文件，不自动发布 artifact；Yue 要求时才发布。交付时把 HTML 复制到项目共享目录 `/mnt/project-files/nook/` 下并附在回复里。
- 雷达和维护报告写给 Yue 看：用 HTML，能用图表就不用大段文字；按“招熟、懂劲、神明”三阶段组织，先讲 20% 最关键的内容。
- 草稿清理与归档规则见 `meta/workflow.md`，写作规范见 `meta/style-guide.md`，动笔前先读。
- 修改章节时同步更新章节开头的状态与“最近更新”日期。
- 提交前运行 `mdbook build` 确认能构建。
