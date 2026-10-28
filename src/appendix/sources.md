# 信息源清单

外部动态雷达所使用的信息源。选源原则是**质量大于数量**：优先一手、原创、有深度的来源。

> 状态：试用期，每周维护一次（新增、降级、移除都记在文末的“变更记录”里）。最近更新：2026-10-28。

## 怎么读这张清单

- **层级**：A = 周三、周六都扫；B = 只在周六扫；C = 每月第一个周六扫。
- **抓取**：RSS / API / 仅网页 / 被挡 / 不可用，均为实测，最近一次在 2026-10-28。被挡的源用搜索补位；“不可用”指源本身有用，但云环境暂时抓不到，每期重试。
- **付费**：💰 表示全部或部分内容需要付费订阅。雷达只读免费部分，付费内容只看标题和导语，是否订阅由 Yue 决定。
- **方向**：通用、AI 产品、金融、医疗。金融和医疗是重点追踪的行业，雷达里单独成节。

## 通用 AI

| 层级 | 信息源 | 类别 | 说明 | 质量评价 | 抓取 | 付费 |
| --- | --- | --- | --- | --- | --- | --- |
| A | [OpenAI News](https://openai.com/news/rss.xml) | 官方博客 | 模型、产品与合作发布；一周约 20 条，过半是客户案例，只留金融、医疗案例和产品发布 | 高 / 信噪比中 | RSS | |
| A | [Anthropic News](https://www.anthropic.com/news) + [Engineering](https://www.anthropic.com/engineering) + [Research](https://www.anthropic.com/research) | 官方博客 | Engineering 栏是 Harness 与 Agent 工程的一手经验；研究长文发在 Research 栏 | 高 / 信噪比高 | 仅网页 | |
| A | [Google DeepMind Blog](https://deepmind.google/blog/rss.xml) | 官方博客 | 科学与医疗方向的研究多 | 高 / 信噪比高 | RSS | |
| A | [Hugging Face Blog](https://huggingface.co/blog/feed.xml) | 开源生态 | 开源模型与训练实践 | 高 / 信噪比中 | RSS | |
| A | [HF Daily Papers](https://huggingface.co/api/daily_papers) | 论文 | 社区投票筛过的 arXiv，按票数取前 10 | 高 / 信噪比高 | API | |
| A | [arXiv cs.CL](https://rss.arxiv.org/rss/cs.CL) / cs.LG / [q-fin](https://rss.arxiv.org/rss/q-fin) | 论文 | 每天上百篇，只用金融、医疗关键词过滤 | 高 / 信噪比低 | RSS | |
| A | [Simon Willison](https://simonwillison.net/atom/everything/) | 个人博客 | 工具与 Agent 实操最快的一手记录 | 高 / 信噪比中 | Atom | |
| A | [Hacker News](https://hn.algolia.com/api/v1/search_by_date?tags=front_page) | 社区讨论 | 只看上过首页的 AI 讨论；原先按 100 分过滤的查询自 10-13 起不再返回新条目，10-25 改为首页查询 | 中 / 信噪比中 | API | |
| A | [GitHub Trending](https://github.com/trending?since=daily)，经 [Trendshift](https://trendshift.io/) 读取 | 开源项目 | 全站榜大半与 AI 无关，只留 AI 相关仓库。GitHub 的 robots.txt 不许抓取工具读 /trending，工具只能返回多年前的旧缓存，所以改读 Trendshift 汇总的每日榜；Trendshift 也抓不到时在雷达附录 C 标“不可用” | 中 / 信噪比低 | 仅网页 | |
| A | [HF Trending](https://huggingface.co/api/trending) | 开源模型 | 社区正在追的模型、Space 和数据集；GitHub Trending 抓不到时由它补位 | 中 / 信噪比中 | API | |
| B | [Import AI](https://importai.substack.com/feed)（Jack Clark） | 周刊 | 研究、政策与安全的解读，每周一更新 | 高 / 信噪比高 | RSS | |
| B | [Interconnects](https://www.interconnects.ai/feed)（Nathan Lambert） | 周刊 | 开源模型与后训练 | 高 / 信噪比高 | RSS | 💰 部分 |
| B | [Latent Space](https://www.latent.space/feed) | 周刊 + 播客 | AI 工程师视角，访谈质量高 | 高 / 信噪比高 | RSS | |
| B | [SemiAnalysis](https://newsletter.semianalysis.com/feed) | 深度分析 | 算力与产业链 | 高 / 信噪比高 | RSS | 💰 部分 |
| B | [量子位](https://www.qbitai.com/feed) | 中文媒体 | 补国内发布动态，标题偏夸张；RSS 只保留约两天，用[首页列表](https://www.qbitai.com/)补齐 | 中 / 信噪比低 | RSS + 网页 | |
| C | [Lilian Weng](https://lilianweng.github.io/index.xml) | 个人博客 | 一年几篇长文，最新一篇讲 Harness Engineering | 极高 | RSS | |

## AI 产品

消费级与 SaaS 方向的 AI 产品方法，和金融、医疗并列的另一条线。

| 层级 | 信息源 | 类别 | 说明 | 质量评价 | 抓取 | 付费 |
| --- | --- | --- | --- | --- | --- | --- |
| B | [Lenny's Newsletter](https://www.lennysnewsletter.com/feed) | 周刊 + 播客 | 一线产品负责人讲具体做法；2026-10-13 至 10-21 的 7 篇里 5 篇讲 AI，如给 Agent 写 PRD、AI 时代的护城河 | 高 / 信噪比高 | RSS | 💰 **部分**：长文与社区精华多为付费，播客免费 |

## 金融 AI

| 层级 | 信息源 | 类别 | 说明 | 质量评价 | 抓取 | 付费 |
| --- | --- | --- | --- | --- | --- | --- |
| A | [Finextra · AI 频道](https://www.finextra.com/rss/channel.aspx?channel=ai) | 行业快讯 | 每天十几条，只看头部机构与产品发布 | 中 / 信噪比中 | RSS | |
| B | [Net Interest](https://www.netinterest.co/feed)（Marc Rubinstein） | 周刊 | 银行、保险、资管的商业逻辑 | 高 / 信噪比高 | RSS | 💰 部分 |
| B | [Fintech Business Weekly](https://fintechbusinessweekly.substack.com/feed)（Jason Mikula） | 周刊 | 美国金融科技监管与合规事件；10-11 之后没有更新，观察中 | 高 / 信噪比中 | RSS | 💰 部分 |
| B | [FSB 金融稳定理事会](https://www.fsb.org/feed/) | 监管 | 只挑 AI 与金融科技条目；2026-10-15 定稿《负责任采用 AI 的良好实践》 | 极高 / 信噪比中 | RSS | |
| C | [Evident AI Index](https://evidentinsights.com) | 研究机构 | 银行与保险业 AI 成熟度排名 | 高 / 信噪比高 | 仅网页 | |
| C | BIS 国际清算银行 | 监管研究 | 央行视角的 AI 与金融稳定研究 | 极高 / 信噪比中 | 被挡 | |

## 医疗 AI

| 层级 | 信息源 | 类别 | 说明 | 质量评价 | 抓取 | 付费 |
| --- | --- | --- | --- | --- | --- | --- |
| A | [STAT · AI 专题](https://www.statnews.com/topic/artificial-intelligence/feed/) | 医疗新闻 | 独立调查报道 | 高 / 信噪比高 | RSS | 💰 部分（STAT+） |
| A | [medRxiv · Health Informatics](https://connect.medrxiv.org/medrxiv_xml.php?subject=Health_Informatics) | 预印本 | 每天十几篇临床 AI 评估，未经评审 | 中 / 信噪比中 | RSS | |
| B | [npj Digital Medicine](https://www.nature.com/npjdigitalmed/research-articles) | 期刊 | 系统综述与临床评估；RSS 停在 08-31，改抓期刊的文章列表页，每天都有新文章 | 高 / 信噪比高 | 仅网页 | |
| B | [Ground Truths](https://erictopol.substack.com/feed)（Eric Topol） | 个人周刊 | 证据导向，近期 AI 文章变少；10-11 之后没有更新，观察中 | 高 / 信噪比中 | RSS | |
| C | [FDA AI 医疗器械清单](https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices) | 监管 | 每月对比新增获批产品 | 极高 / 信噪比高 | CSV 下载 | |
| C | NEJM AI | 期刊 | 临床 AI 顶刊 | 极高 / 信噪比高 | 被挡 | 💰 部分 |
| C | [Stanford RAISE Health](https://med.stanford.edu/raisehealth/news/newsletter.html) | 月刊 | 负责任的医疗 AI | 高 / 信噪比高 | 仅网页 | |

## 扫描组合

| 扫描 | 时间窗口 | 范围 | 产出上限 |
| --- | --- | --- | --- |
| 周三 | 上周六 → 周三 | A 层 | 精选 10 条 |
| 周六 | 周三 → 周六 | A 层 + B 层 | 精选 15 条 |
| 每月第一个周六 | 上个月 | 另加 C 层 | 另加 5 条 |

arXiv 过滤关键词：

- 金融：financial, banking, credit, fraud, risk, trading, insurance, compliance
- 医疗：clinical, medical, EHR, radiology, diagnosis, patient, healthcare

## 未收录

| 信息源 | 原因 |
| --- | --- |
| TLDR AI、The Rundown、The Neuron、Ben's Bites | 二手摘要，太短、广告多，与一手源重复 |
| AINews（smol.ai） | feed 最新一条停在 2026-09-09，排序颠倒 |
| 机器之心 | 没有可用的 RSS，量子位已覆盖同类内容 |
| Healthcare IT News | AI 页最新内容停在 2026-06 |
| The Information、Stratechery | 💰 全付费，质量高，是否订阅由 Yue 决定 |
| 播客（Dwarkesh、No Priors 等） | 音频难摘要，干货会被周刊转述，按需收听 |

## 变更记录

| 日期 | 变更 |
| --- | --- |
| 2026-10-28 | GitHub Trending 改经 Trendshift 读取，恢复可用：查明旧榜单来自抓取工具的缓存，GitHub 的 robots.txt 禁止抓取工具读 /trending |
| 2026-10-28 | 按 Yue 意见恢复 GitHub Trending：榜单本身有用，问题出在云环境的抓取（旧缓存、直连被挡），保留在 A 层，标“不可用”，每期重试；HF Trending 保留补位 |
| 2026-10-25 | 第二次维护：GitHub Trending 失效，移除，由 HF Trending 接替；Hacker News 改为首页查询；npj Digital Medicine 改抓文章列表页；量子位加抓首页列表；Fintech Business Weekly、Ground Truths 两周未更新，继续观察 |
| 2026-10-23 | 首次维护：Anthropic 增加 Research 栏目（形式化验证一文只发在这里）；OpenAI News 写明过滤规则 |
| 2026-10-23 | 首版：29 个源，A 层 12、B 层 11、C 层 6；新增 AI 产品方向，收录 Lenny's Newsletter |
