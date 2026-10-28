# 外部动态雷达

每周三、周六各一期，扫描 AI 领域的高质量信息源，挑出值得关注、值得入书的内容。信息源清单见 [`src/appendix/sources.md`](../src/appendix/sources.md)。

## 规则

- 按年份归档：`radar/2026/2026-10-24.html`，文件名为发布日期。
- 复制 [`_template.html`](_template.html) 生成每期内容，模板开头的注释是写法规则。默认只产出 HTML 文件，不自动发布 artifact，Yue 要求时才发布。
- 按“招熟、懂劲、神明”三阶段组织：先给 1 到 3 条“本期必懂”，每条信号标出阶段，术语首次出现附英文。
- 每期条目宁缺毋滥，每条说明“为什么重要”和“建议归入的章节”。
- 合并到 main 后自动发布到 <https://lyteboat.github.io/nook/>：构建脚本扫描 `radar/YYYY/YYYY-MM-DD.html`，按日期倒序生成首页目录，首页标题取每期的 h1。站点有三部分：首页是最新一期的简报（一句话结论、刊头数字、本期必懂的心法和招式、按行业分栏的条目速览），以及往期列表；“全部条目”页汇总每期附录 A 的条目总表，可搜索，可按行业、阶段、技术标签筛选；每期页面左侧是本期章节目录和全部期数。这些内容都从模板里固定的 class 和附录 A 表格自动提取，写雷达时保持模板结构即可。文件名不符合这个格式的不会发布。
- 雷达存档**长期保留**，不做清理；它是书稿的参考素材库。
- 标记为“建议入书”的条目，经确认后转为草稿或直接写进章节，并在本期文件里注明去向。

## 技术标签词表

附录 A 条目总表里，“行业”只分通用、金融、医疗；“标签”标技术主题，每条一到三个，用顿号分隔。站点“全部条目”页按这两列筛选。新标签先补进下表再用，同一个概念只用一个写法。

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
