# Nook 仓库约定

这是 Yue 的 AI 学习之书《Nook：我的 AI 指南针》，用 mdBook 构建，正文使用简体中文。

- 正式书稿在 `src/`，目录在 `src/SUMMARY.md`。新增或移动章节必须同步更新 `SUMMARY.md`，并在 `src/appendix/changelog.md` 记录。
- 未成形的内容放 `drafts/inbox/`，用 `drafts/_template.md`，文件名 `YYYY-MM-DD-主题.md`。不要把草稿直接写进 `src/`。
- 以后要深入研究的话题和暂时没空展开的零碎想法，记进 `meta/backlog.md`（待研究清单，类似待办清单）：原话照录，不展开讨论，新条目追加在“待研究”末尾。它不属于草稿池，不参加草稿盘点。我说“记一下”“以后再看”之类的话时，默认记到这里。
- 外部动态雷达放 `radar/YYYY/YYYY-MM-DD.html`，用 `radar/_template.html`，每周三、周六各一期。
- 每周维护报告放 `meta/maintenance/YYYY-MM-DD.html`，用 `meta/maintenance/_template.html`，每周日一份。交付时把 HTML 复制到项目共享目录 `/mnt/project-files/nook/` 下并附在回复里。
- 雷达和维护报告写给 Yue 看：用 HTML，能用图表就不用大段文字；按“招熟、懂劲、神明”三阶段组织，先讲 20% 最关键的内容。
- 草稿清理与归档规则见 `meta/workflow.md`，写作规范见 `meta/style-guide.md`，动笔前先读。
- 讲解和写作前先读 `meta/learner.md`：我是熟悉 Java、C#、Python 的传统工程师，做过少量后训练。按“招熟、懂劲、神明”三阶段回答，先招熟再懂劲，神明点到为止；每阶段分心法和招式，招式 5 到 9 项；二八原则，简洁、举例，关键术语附英文。
- 我提出问题或概念时，按 `meta/roles.md` 进行：三个角色（风清扬讲解、周伯通提问、王语嫣记录）先在内部头脑风暴，**过程不展示给我**；直接交付第一版报告（用 `drafts/_template-study.html` 写成 HTML，多用 C4 图、架构图、流程图和表格，最后附“过招中的好问题”），我再据此追问，Claude 回答并修订报告。不开子代理。
- 产出默认生成文件（HTML、Markdown 等），写进仓库或作为附件发给我。**不要自动发布 Artifact**，只有我明确要求时才发布，因为 Artifact 需要我自己手动维护和删除。
- 修改章节时同步更新章节开头的状态与“最近更新”日期。
- 提交前运行 `mdbook build` 确认能构建。
