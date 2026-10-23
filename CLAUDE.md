# Nook 仓库约定

这是 Yue 的 AI 学习之书《Nook：我的 AI 指南针》，用 mdBook 构建，正文使用简体中文。

- 正式书稿在 `src/`，目录在 `src/SUMMARY.md`。新增或移动章节必须同步更新 `SUMMARY.md`，并在 `src/appendix/changelog.md` 记录。
- 未成形的内容放 `drafts/inbox/`，用 `drafts/_template.md`，文件名 `YYYY-MM-DD-主题.md`。不要把草稿直接写进 `src/`。
- 以后要深入研究的话题和暂时没空展开的零碎想法，记进 `meta/backlog.md`（待研究清单，类似待办清单）：原话照录，不展开讨论，新条目追加在“待研究”末尾。它不属于草稿池，不参加草稿盘点。我说“记一下”“以后再看”之类的话时，默认记到这里。
- 外部动态雷达放 `radar/YYYY/YYYY-MM-DD.md`，用 `radar/_template.md`，每周三、周六各一期。
- 草稿清理与归档规则见 `meta/workflow.md`，写作规范见 `meta/style-guide.md`，动笔前先读。
- 讲解和写作前先读 `meta/learner.md`：我是熟悉 Java、C#、Python 的传统工程师，做过少量后训练。按“招熟、懂劲、神明”三阶段回答，先招熟再懂劲，神明点到为止；每阶段分心法和招式，招式 5 到 9 项；二八原则，简洁、举例，关键术语附英文。
- 我提出问题或概念要讨论时，按 `meta/roles.md` 的三个角色（风清扬讲解、周伯通提问、王语嫣记录）和工作流进行：在同一个 thread 里切换角色，不开子代理；每轮留一个问题给我，我说“收”后用 `drafts/_template-study.html` 整理成 HTML 草稿，多用 C4 图、架构图、流程图和表格说明。
- 产出默认生成文件（HTML、Markdown 等），写进仓库或作为附件发给我。**不要自动发布 Artifact**，只有我明确要求时才发布，因为 Artifact 需要我自己手动维护和删除。
- 修改章节时同步更新章节开头的状态与“最近更新”日期。
- 提交前运行 `mdbook build` 确认能构建。
