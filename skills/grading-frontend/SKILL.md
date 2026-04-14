---
name: grading-frontend
description: Grade a team's frontend implementation against its spec on 10 weighted dimensions, producing a markdown report + JSON summary with evidence.
---

# grading-frontend

给 AI 培训项目前端实现打分。50 学员分成 ~12 组，按 spec-driven 方式实现本地部署的网站。本 skill 让 Claude（或 Qoder / Cursor / Claude Code agent）按统一 rubric 给某一组的前端打分，产出可给学员的 markdown 报告 + 可汇总 leaderboard 的 JSON。

---

## 前置依赖

- **本地可跑**：待评项目能在本机 `npm run dev` / `pnpm dev` / `yarn dev` 启动，默认 `http://localhost:3000`（按项目 README 调整）。
- **Spec 文档位置**：`<project>/docs/spec.md` 或 `<project>/README.md` 或 `<project>/spec/*`。找不到则先向用户确认 spec 路径再开工，不要凭空评分。
- **Node.js 环境**：Node ≥ 18，用来跑 `npx playwright-cli` 截图、`npx ajv-cli` 校验 JSON。首次使用时 `npx playwright install chromium`。
- **输出目录**：所有证据和报告写到待评项目根目录下的 `.grading/`（已由 spec 约定 gitignore）。

---

## 共享契约（必读）

评分开始前，**必须先读完** `skills/grading-shared/` 下 4 个文件。这些是 frontend / backend 两个 skill 共用的硬约束，不读会导致输出格式不一致、无法汇总 leaderboard：

1. `../grading-shared/rubric-scale.md` — 0–10 标尺含义 + S/A/B/C/D 档位定义。**所有维度打分必须对照此标尺**。
2. `../grading-shared/report-template.md` — 统一 Markdown 报告模板。产出的 `report.md` 必须照此结构填充。
3. `../grading-shared/score-schema.json` — JSON 摘要的 schema。产出的 `summary.json` 必须通过此 schema 校验。
4. `../grading-shared/evidence-requirements.md` — 证据硬约束（打分 ≥7 或 ≤4 必须 ≥2 条证据，5–6 分必须 ≥1 条）。违反则打分视为无效。

---

## 配套资源

按需读取（不是每次都读全部）：

- **`./anti-patterns.md`** — AI slop 前端反模式清单。**打"主题与审美"和"代码质量"两个维度时必读**，用来识别默认 shadcn 灰白调、无主题色、按钮都 `bg-blue-500`、空态只写 "No data" 等典型滑坡。
- **`./examples/good-report.md`** 和 **`./examples/mediocre-report.md`** — 两份标定样例报告。**打分前读一次做分布校准**，避免全班都打 8 分这种分不开档的问题。
- **`./probes/probe-screenshots.sh`** — 批量跑 4 态 + 3 断点截图（login / dashboard / empty / error × desktop / tablet / mobile）。取证时直接 `bash ./probes/probe-screenshots.sh <team> <base-url>` 即可，不要手搓 playwright 命令。
- **`./probes/probe-performance.sh`** — 跑 Lighthouse 或 `curl -w` 测 TTFB / FCP 数据，输出到 `.grading/probes/<team>-perf.log`。
- **`./probes/probe-a11y.sh`** — 跑 axe-core CLI 扫关键页面的 a11y 违规项，输出到 `.grading/probes/<team>-a11y.log`。

---

## 评分流程（5 步）

### 步骤 1：定位与启动

1. 确认 spec 路径，记录 `spec_sha`（若 spec 在 git 仓库内）。
2. 读完 spec，列出：路由清单 / 核心组件 / 主流程（登录、提交、列表、详情、管理等）。
3. 读 `package.json` 识别技术栈（React/Vue、TS/JS、Tailwind/CSS-in-JS、状态管理等），记录 `project_sha`。
4. 启动 dev server，确认 `http://localhost:<port>` 可访问。

### 步骤 2：收集证据（evidence-first）

**静态证据**：
- 用 Grep/Glob 扫组件树、路由表、全局样式、TS 类型、状态管理。
- 为每个维度预留至少 1 处 `file:line` 引用。

**动态证据**：
```bash
# 一次性把主要页面的 3 断点 × 4 态截图跑完
bash ./probes/probe-screenshots.sh <team> http://localhost:3000

# 性能 & a11y
bash ./probes/probe-performance.sh <team> http://localhost:3000
bash ./probes/probe-a11y.sh <team> http://localhost:3000
```

所有截图落到 `.grading/shots/<team>-*.png`，所有 probe 日志落到 `.grading/probes/<team>-*.log`。

如果 `playwright-cli` 不可用，fallback 为：提示评分人手动放置截图到 `.grading/shots/` 后再继续。

**交互证据**：手动或用 playwright 过一遍主流程（登录 → 核心 CRUD → 提交 → 错误路径），记录 console / network 异常。

### 步骤 3：按 10 维度逐条打分

对照本文件下方 rubric（以及 `../grading-shared/rubric-scale.md`），逐维度 0–10 打分。每一条打分必须附证据（file:line / 截图路径 / probe log 行号）。spec 未要求的维度写 "N/A — 原因"，不计入总分。

### 步骤 4：产出 report.md + summary.json

按 `../grading-shared/report-template.md` 模板填 `.grading/reports/<team>-frontend.md`；按 `../grading-shared/score-schema.json` 填 `.grading/reports/<team>-frontend.json`。每维度附"要到 10 差什么"2–4 条。

### 步骤 5：自检（必须通过）

```bash
# JSON schema 校验
npx ajv-cli validate -s skills/grading-shared/score-schema.json \
  -d .grading/reports/<team>-frontend.json

# 证据数量自检（每维度统计 file:line + 截图 + log 引用总数）
grep -cE "\.(tsx?|jsx?|vue|css|png|log):" .grading/reports/<team>-frontend.md
```

自检不过则回到步骤 2 补证据，不得放过。

---

## 10 个评分维度（权重合计 100）

| # | 维度 | 权重 |
|---|---|---:|
| 1 | Spec 一致性 | 20 |
| 2 | 主题与审美 | 12 |
| 3 | 动画与流畅度 | 10 |
| 4 | 状态完备性 | 10 |
| 5 | 代码质量 | 10 |
| 6 | 响应式适配 | 8 |
| 7 | 表单与输入反馈 | 8 |
| 8 | 性能 | 8 |
| 9 | 无障碍 (a11y) | 8 |
| 10 | 微文案 | 6 |

---

### 1. Spec 一致性（权重 20）

**关注点**
- spec 列出的每一条路由 / 页面 / 组件是否都实现了。
- 核心流程字段、状态、文案是否与 spec 对齐，没有偷工减料也没有无关超纲。
- 权限 / 角色分支（如管理员页面）是否完整。

**锚点**
- 10：spec 列出的所有页面和流程 100% 实现；字段、状态码、文案与 spec 完全一致；超纲功能明确标注为增强。
- 7：主流程对齐，但遗漏 1–2 个次要页面或 2–3 处字段细节。
- 5：核心页面都在，但多处字段偏离 spec，或 1 个关键流程（如提交 / 审核）未实现。
- 3：大段偏离 spec，或只实现了 demo 页面，真实业务流程缺失。

**取证方法**
1. 把 spec 的路由清单和 `src/routes` / `app/` 目录对应关系列表。
2. 核心流程逐步点一遍，截图 + 对照 spec 条款。
3. 对每个缺失项记录 spec 章节号 + 期望行为。

**证据要求**
- 至少 3 条 `file:line` 引用到组件 / 路由文件。
- 至少 2 张主流程截图。
- 一张 spec vs 实现的对齐表（在报告里用 markdown 表格）。

---

### 2. 主题与审美（权重 12）

**关注点**
- 配色是否有主题色，不是一地灰白。
- 字体、字号层次、间距是否成体系（不是全用默认）。
- 卡片、阴影、圆角是否有设计感（不是默认 `rounded-lg shadow`）。
- AI slop 味（见 `./anti-patterns.md`）。

**锚点**
- 10：有明确主题色系（主 / 辅 / 强调），自定义字体栈，间距节奏一致，视觉层次清晰到像一个真产品。
- 7：有基本主题色和字体选择，多数页面一致，但 1–2 个页面掉档或默认组件未改皮。
- 5：能看出改过样式，但主题不明、灰白主导，大量 shadcn 默认外观。
- 3：通篇灰白 + 默认 `bg-blue-500` 按钮 + `gray-100` 背景，典型 AI slop。

**取证方法**
1. 读 `./anti-patterns.md`，对照本项目截图逐条判断命中了哪些反模式。
2. 看 `tailwind.config.*` / `theme/*` / 全局 CSS，确认是否真的定义了主题 token。
3. 多张截图拼对比：不同页面的按钮、卡片、标题层次是否一致。

**证据要求**
- 至少 3 张截图覆盖 3 个不同页面。
- 至少 1 条 `tailwind.config.*:line` 或 `theme.ts:line` 的引用。
- 反模式命中清单（至少覆盖 `anti-patterns.md` 中前 5 条）。

---

### 3. 动画与流畅度（权重 10）

**关注点**
- 页面切换 / 弹窗 / Toast / 菜单的过渡是否自然，不是突变。
- 微交互（hover、按压、图标反馈）是否有。
- 无明显 layout shift，列表加载不跳动。
- 主交互保持 60fps，不卡顿。

**锚点**
- 10：关键过渡用 spring / cubic-bezier，有进入 / 离开动画；微交互覆盖主要按钮；无 layout shift；滚动和拖拽流畅。
- 7：主要过渡做了 fade / slide，微交互覆盖部分按钮，偶有 1–2 处抖动。
- 5：只有默认 Tailwind `transition`，弹窗 / 路由硬切，hover 仅变色。
- 3：零动画，UI 突变，列表加载瞬间 reflow 一大片。

**取证方法**
1. 录屏或跑 playwright 的 trace（`--trace on`）观察过渡。
2. 搜 `transition` / `motion` / `framer-motion` / `@keyframes` 的使用。
3. 在 DevTools Performance 面板看关键交互的 FPS。

**证据要求**
- 至少 1 段 trace 截图或录屏帧。
- 至少 2 条 `file:line` 证明动画实现（或证明没有）。

---

### 4. 状态完备性（权重 10）

**关注点**
- loading / empty / error / success 四态在关键列表和详情页是否都覆盖。
- loading 有 skeleton 或 spinner，不白屏。
- empty 有引导（不只是 "No data"）。
- error 有可操作出路（重试、返回）。

**锚点**
- 10：所有主要数据组件都实现了 4 态，空态有插画或引导 CTA，错误态有重试按钮且区分网络 / 业务错误。
- 7：主流程四态到位，但 1–2 个次要页面缺 empty 或 error。
- 5：只有 loading + success，empty 是 "No data"，error 是 `alert(err)`。
- 3：接口慢就白屏，接口错就崩白页或 console 报错。

**取证方法**
1. 用 DevTools Network 面板把关键接口设为 Slow 3G + 手动 Fail，分别截图。
2. 把数据清空 / mock 空数组看 empty 态。
3. `bash ./probes/probe-screenshots.sh` 已内置 empty / error view 的路由截图。

**证据要求**
- 至少 4 张截图覆盖 loading / empty / error / success。
- 至少 2 条 `file:line` 引用组件的状态分支代码。

---

### 5. 代码质量（权重 10）

**关注点**
- 组件拆分粒度合理（不是一个 500 行的巨型组件）。
- TypeScript 类型真实有效，不是满屏 `any`。
- hooks 使用正确（依赖数组齐全，无不必要 re-render）。
- 没有严重 prop drilling，状态管理有章法。
- 复用度（公共组件、常量、工具函数）。

**锚点**
- 10：目录分层清晰，组件 ≤ 200 行，类型覆盖 100%，hooks 无警告，状态管理边界清楚，复用充分。
- 7：整体干净，偶有 1–2 处 `any` 或轻微 prop drilling，但架构能看懂。
- 5：能跑，但有巨型组件或 `any` 满天飞，hooks 依赖数组乱填。
- 3：意大利面式代码，大量 console.log，类型形同虚设，复制粘贴成灾。

**取证方法**
1. Grep `any`、`@ts-ignore`、`console.log` 数量。
2. 按文件行数排序，挑最长的几个 component 文件看。
3. 抽 2–3 个 hook 检查依赖数组。
4. 对照 `./anti-patterns.md` 中的前端代码反模式。

**证据要求**
- 至少 4 条 `file:line` 引用（好的和差的都要有）。
- 一组 grep 统计数据（any / ts-ignore / console.log 计数）。

---

### 6. 响应式适配（权重 8）

**关注点**
- desktop (≥1280) / tablet (768–1279) / mobile (<768) 三个断点都能看、能用。
- 布局不断裂，按钮不压成一坨。
- 手势和触达（最小 44px 触控区域）。

**锚点**
- 10：三断点均精心布局，mobile 有专门导航（抽屉 / tab bar），内容优先级调整合理。
- 7：三断点可用，但 mobile 多处拥挤或需要横向滚动。
- 5：只在 desktop 看着正常，mobile 勉强能用但布局错乱。
- 3：只做 desktop，mobile 直接溢出 / 重叠 / 不可点。

**取证方法**
1. `bash ./probes/probe-screenshots.sh` 已生成 3 断点截图。
2. 查 `tailwind.config` 断点设置和组件里 `sm:` / `md:` / `lg:` 分布。

**证据要求**
- 3 断点 × 至少 2 个页面 = 至少 6 张截图。
- 至少 2 条 `file:line` 体现断点处理代码。

---

### 7. 表单与输入反馈（权重 8）

**关注点**
- 客户端校验（必填、格式、长度）。
- 错误提示贴近字段，不是 alert。
- 提交过程中按钮禁用 + loading，防重复提交。
- 成功后有明确反馈（toast / 跳转 / inline success）。

**锚点**
- 10：全表单含行内校验 + 提交防抖 + 成功态 toast，键盘可 tab 过全部字段，有 `aria-invalid` 标注。
- 7：主表单有基本校验和禁用态，1–2 处错误提示样式不统一。
- 5：只有后端兜底校验，错误用 alert，能双击提交产生两条记录。
- 3：没校验，没禁用，错了崩掉，没有任何反馈。

**取证方法**
1. 对每个表单跑：空提交 / 非法格式 / 超长字段 / 快速连点提交，截图 + 录 network。
2. 搜 `useForm` / `zod` / `yup` / `disabled` / `isSubmitting` 的使用。

**证据要求**
- 至少 3 张截图（空提交 / 非法 / 成功）。
- 至少 2 条 `file:line` 引用校验逻辑。
- 一条 network log 证明是否防重复提交。

---

### 8. 性能（权重 8）

**关注点**
- 首屏 TTFB + FCP + LCP 合理（本地 dev 下 LCP < 2s 可接受）。
- bundle 体积合理，无重复依赖、无未用的大库。
- 长列表虚拟化、图片懒加载。
- 交互响应（INP）流畅。

**锚点**
- 10：Lighthouse Performance ≥ 90（本地 dev 下），关键页面 LCP < 1.5s，bundle < 500KB gzip，长列表虚拟化。
- 7：Lighthouse 75–89，有明显可优化点但不影响体验。
- 5：Lighthouse 50–74，首屏偏慢或 bundle 臃肿（> 1MB gzip 无理由）。
- 3：Lighthouse < 50，切页面要等几秒，JS 主线程长期占满。

**取证方法**
1. `bash ./probes/probe-performance.sh` 生成 TTFB / FCP / LCP 数据。
2. `npm run build` 看产物大小；`npx source-map-explorer` 看 bundle 组成（可选）。
3. 搜 `React.lazy` / `import()` / `loading="lazy"` / 虚拟列表库使用。

**证据要求**
- 至少 1 份 probe-performance.log。
- 至少 1 条 build 产物大小数据。
- 至少 2 条 `file:line` 体现优化手段或缺失。

---

### 9. 无障碍 a11y（权重 8）

**关注点**
- 键盘可导航（Tab 顺序合理，焦点可见）。
- 语义化标签（button / a / label / heading 层级）。
- 颜色对比度达 WCAG AA（正文 4.5:1，大字 3:1）。
- ARIA 属性用对（不滥用）。
- `focus-visible` 样式存在。

**锚点**
- 10：axe 扫描零严重违规，全键盘可操作，`focus-visible` 清晰，表单有 label 关联，对比度全过。
- 7：axe 有 1–2 条中等违规，键盘可用但焦点环偶尔消失。
- 5：多条对比度不足，部分按钮用 `<div>`，无 `focus-visible`。
- 3：大量 `<div onClick>`，Tab 键按下去什么都不响应。

**取证方法**
1. `bash ./probes/probe-a11y.sh` 跑 axe-core，看违规清单。
2. 手动 Tab 一遍关键页面。
3. 搜 `role=` / `aria-` / `focus-visible` / `<label` 的使用密度。

**证据要求**
- 1 份 probe-a11y.log。
- 至少 2 条 `file:line` 引用（正或反面）。
- 至少 1 张键盘焦点截图。

---

### 10. 微文案（权重 6）

**关注点**
- 按钮文案是动词 + 对象，不是 "OK" / "Submit"。
- 空态文案告诉用户下一步做什么。
- 错误信息具体且可操作（不是 "Something went wrong"）。
- 文案风格统一（全站同一人称、同一语气）。

**锚点**
- 10：所有按钮、空态、错误态的文案都经过润色，一致、具体、有品牌语气。
- 7：关键按钮和空态文案良好，但错误信息偶有通用模板。
- 5：按钮是 "提交" / "确定"，空态是 "暂无数据"，错误是 "操作失败"。
- 3：混用中英文，或全英文但像机翻，文案语气不统一。

**取证方法**
1. 把所有按钮 / 空态 / 错误文案抽样列表（grep 关键 string）。
2. 看同一操作在不同页面的按钮文案是否一致。

**证据要求**
- 至少 1 份文案抽样表（按钮 / 空态 / 错误 各 ≥ 3 条）。
- 至少 2 条 `file:line` 引用具体文案位置。

---

## 产出 checklist

评分结束前逐项勾选，任一不通过就回到相应步骤补齐：

- [ ] `.grading/reports/<team>-frontend.md` 已按 `../grading-shared/report-template.md` 结构填完，10 个维度全部评完（或明确标 N/A）。
- [ ] `.grading/reports/<team>-frontend.json` 已产出，并通过 `npx ajv-cli validate -s skills/grading-shared/score-schema.json` 校验。
- [ ] 每个维度都有证据引用，且满足 `../grading-shared/evidence-requirements.md` 硬约束（≥7 / ≤4 分 ≥2 条；5–6 分 ≥1 条）。
- [ ] `.grading/shots/` 含至少 3 断点 × 4 态的截图；`.grading/probes/` 含 perf + a11y 两份 log。
- [ ] 报告末尾给出"最该优先修的 3 件事"，每条对应到具体维度和 file:line。
