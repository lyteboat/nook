# 随笔

Yue 自己写的经验、复盘和零碎的想法，和雷达是两个独立模块，不定期更新。

- 每篇一个 Markdown 文件：`notes/YYYY/YYYY-MM-DD-英文短名.md`，复制 [`_template.md`](_template.md)。开头两行 `---` 之间写「写法」「状态」和「引用」，下面用 `#` 写标题，再写正文。在线编辑页写的随笔把标题放在文件头的「标题」里，两种写法都认。
- 写法分四种：札记、长文、复盘、过招。
- 构建脚本把 Markdown 转成 HTML，样式由站点统一提供。支持标题、段落、列表、引用、代码块、分隔线、加粗、斜体、链接和图片。需要更复杂的版式时，也可以直接写 HTML 片段（`.html`，用 `<article class="note" data-kind="札记">` 包住 h1 和正文）。
- 状态为「草稿」的不发布，其余合并到 main 后自动发布：首页底部列最新 6 篇，“随笔”页按年列出全部，每篇有自己的页面和上一篇、下一篇翻页。文件名不符合格式的不会发布。

## 新建和修改

- 在线编辑（推荐）：打开 <https://lyteboat.github.io/nook/admin/>，第一次在这台设备上点「使用访问令牌登录」，粘贴 GitHub 令牌。「使用 GitHub 登录」按钮要另配登录中转，目前用不了。之后可以新建、修改、删除随笔和上传图片。每次保存直接提交到 main，1 到 2 分钟后站点更新。
  - 状态选「草稿」的不上站点，改成「已发布」再保存，所有人不用登录就能看。草稿只是不上站点，仓库是公开的，在 GitHub 上仍看得到。
  - 新随笔的文件名由新建那天的日期和「英文短名」生成，建好后不再改名；图片存在 `notes/images/`。
  - 令牌在 <https://github.com/settings/personal-access-tokens/new> 建：Resource owner 选 lyteboat，Repository access 只选 nook，Permissions 里 Contents 设为 Read and write，有效期最长一年，过期后重建一个再登录。
- 在 GitHub 网页上：进 `notes/` 目录点 Add file → Create new file，文件名填 `2026/2026-11-06-xxx.md`，粘贴模板改写后提交。改旧文章就打开那篇点铅笔图标。网页编辑器有 Preview 页签，可以先看效果。
- 交给 Claude：把要写的内容发给它，说“记成随笔”，它按模板整理好开 PR。
