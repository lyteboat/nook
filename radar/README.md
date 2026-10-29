# 外部动态雷达

每周三、周六各一期，扫描 AI 领域的高质量信息源，挑出值得关注、值得入书的内容。信息源清单见 [`src/appendix/sources.md`](../src/appendix/sources.md)。

## 规则

- 按年份归档：`radar/2026/2026-10-24.html`，文件名为发布日期。
- 复制 [`_template.html`](_template.html) 生成每期内容，模板开头的注释是写法规则。默认只产出 HTML 文件，不自动发布 artifact，Yue 要求时才发布。
- 每个条目的标题写“主体｜做了什么”，副标题写意义，首页速览和期刊页用同一个标题，写法见模板注释第 2 条。正文固定为六栏：What 是什么、Why 为什么重要、How 怎么做的、Who 谁、When 何时、Action 我们做什么，末尾附原文标题和链接，标题照录不翻译。页面只放结论和事实；打分、原文核对、草稿盘点这些编辑过程写进同名的 `YYYY-MM-DD.notes.html`，不发布。
- 每条标出“招熟、懂劲、神明”阶段；本期必看是技术、产品两条线各取前二。
- 合并到 main 后自动发布到 <https://lyteboat.github.io/nook/>，构建脚本是 `scripts/build_site.py`。站点分雷达和随笔两个模块，菜单一行：本期、专题、全部条目、往期，竖线后是随笔。首页是最新一期的标题和一句话结论，挂上本期专题，再是本期速览：技术、产品两栏，每条一行短标题，按重要程度排序，必看四条标“必看”，不另设必看卡片；页面底部列最新的随笔。每期页面是雷达原文：必看四条展开，其余条目折叠成标题和副标题两行、点开看六栏，再加本期行动，带上一期、下一期翻页；附录 A 是站点的数据源，页面上不显示。“全部条目”页汇总每期附录 A，可搜索，可按轨道、行业、阶段、标签筛选；“往期”页列每期的标题、一句话结论和专题，点进每期页面。这些内容都从模板里固定的 class 和附录 A 表格自动提取，写雷达时保持模板结构即可。首页速览和全部条目页里的条目可以点，跳到正文里讲这一条的位置：附录 A 的条目单元格写成 `<a href="#i-slug">`，正文对应元素加 `id="i-slug"`；没写锚点的条目跳到这一期的开头。专题放 `topics/YYYY/YYYY-MM-DD-英文短名.html`，封面的 `data-after` 写接在哪一期之后，`data-tags` 用于汇总雷达里的相关条目；随笔的写法见 [`notes/README.md`](../notes/README.md)。文件名不符合格式的不会发布。
- 雷达存档**长期保留**，不做清理；它是书稿的参考素材库。
- 标记为“建议入书”的条目，经确认后转为草稿或直接写进章节，并在本期文件里注明去向。

## 技术标签词表

附录 A 条目总表里，“轨道”只分技术、产品，“总分”填编辑部打分；“行业”只分通用、金融、医疗；“标签”标技术主题，每条一到三个，用顿号分隔。站点“全部条目”页按这两列筛选。新标签先补进下表再用，同一个概念只用一个写法。

| 标签 | 含义 |
|---|---|
| Agent | 智能体（Agent）的能力、落地与权限设计 |
| 多智能体 | 多智能体协作与编排（Multi-Agent） |
| MCP | 模型上下文协议（Model Context Protocol）与工具调用 |
| Skills | Agent 技能包（Agent Skills） |
| 沙箱 | Agent 运行时隔离（Sandbox） |
| 权限 | Agent 的授权、只读与审批边界 |
| RAG | 检索增强生成（Retrieval-Augmented Generation） |
| 后训练 | 微调、RLHF 等后训练（Post-training） |
| RLVR | 可验证奖励的强化学习（RL with Verifiable Rewards） |
| 评测 | 基准与评测方法（Evaluation、Benchmark） |
| LLM 评审 | 用模型做评审（LLM-as-a-Judge） |
| 安全对齐 | 安全与对齐（Safety、Alignment） |
| 人机协作 | 人在回路（Human-in-the-loop）与人工审核 |
| 形式化验证 | 形式化验证（Formal Verification） |
| AI 编程 | 代码生成与编程 Agent（AI Coding） |
| RSI | 递归自我改进（Recursive Self-Improvement），AI 研究 AI |
| 模型发布 | 新模型与版本发布 |
| 算力 | 芯片、算力与供应链（Compute） |
| AI for Science | 科研领域的 AI 应用 |
| 标准 | 开放标准与中立机构 |
| 监管 | 法规、监管与治理（Regulation、Governance） |
| 产品化 | 产品打法、留存与交付（Productization） |
| 用户研究 | 用户调查与采纳研究 |
| 支付 | Agent 支付（Agentic Payments） |
| 产业 | 并购、裁员、组织与市场格局 |
