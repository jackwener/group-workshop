# 前端作业反模式清单

本文件列出学员作业中常见的"坏味道"与 AI slop 特征。grading agent 在评分前应过一遍本清单，按条取证、按维度扣分。每条格式为：

- **反模式名**：一句话说明为什么坏
  - *取证*：具体 grep / 截图步骤
  - *影响维度*：受影响的 rubric 维度及扣分建议

---

## 1. AI slop（视觉 / 调色板）

- **全灰灰白白调色板**：整站被 Tailwind `gray-*` 吃掉，没有任何品牌色记忆点，像 shadcn demo 的默认截图。
  - *取证*：`grep -rEn "(bg|text|border)-(gray|slate|zinc|neutral|stone)-" src/ | wc -l` 与 `grep -rEn "(bg|text|border)-" src/ | wc -l` 比值 ≥ 0.7；再截 3 张首页/详情/表单确认通篇灰白。
  - *影响维度*：主题审美 -2；视觉一致性 -1。

- **默认 shadcn 未改主题**：安装了 shadcn 但 `globals.css` / `tailwind.config.*` 的 CSS variables 仍是官方默认值，`--primary` 还是黑色。
  - *取证*：`grep -n "\-\-primary\|\-\-accent\|\-\-ring" src/**/*.css app/**/*.css`；比对 shadcn 官方初始值，若 100% 相同则判定未改。
  - *影响维度*：主题审美 -2；品牌识别 -1。

- **千篇一律的卡片**：所有卡片都是 `rounded-lg shadow p-4 bg-white`，没有层级、没有强调、没有变体。
  - *取证*：`grep -rEn "rounded-(md|lg|xl)\s+shadow(-sm|-md)?\s+" src/ | sort -u | head -20`，若 80% 卡片结构一致则命中。
  - *影响维度*：信息层级 -2；视觉节奏 -1。

- **万年 primary 蓝按钮**：所有按钮都是 `bg-blue-500 hover:bg-blue-600 text-white`，复制粘贴感强烈。
  - *取证*：`grep -rEn "bg-blue-(500|600)" src/ | wc -l`；截图确认 CTA / 次级按钮 / destructive 按钮都用了同一个蓝。
  - *影响维度*：交互层级 -1；主题审美 -1。

- **无自定义 theme**：`tailwind.config.*` 的 `theme.extend` 为空对象或缺失 `colors` / `fontFamily` / `spacing` 扩展。
  - *取证*：读 `tailwind.config.{js,ts,mjs}`，检查 `theme.extend` 字段；若只有默认或注释示例则命中。
  - *影响维度*：主题审美 -1；工程完整度 -1。

- **单一字号**：整页文本只有一两个字号，无 H1/H2/正文/辅助文字的层级。
  - *取证*：`grep -rEn "text-(xs|sm|base|lg|xl|2xl|3xl|4xl)" src/ | awk '{print $2}' | sort -u`，种类 ≤ 2 即命中；截图看最大标题和正文差距。
  - *影响维度*：信息层级 -2；可读性 -1。

- **emoji 替代图标**：关键 UI 处（导航、按钮、状态）用 emoji 充当图标，未引入 lucide / heroicons。
  - *取证*：`grep -rEn "[🔥✨🎉📊📁🚀]|&#x1F" src/ app/ components/`；统计出现在非文案类元素（按钮、nav、badge）中的次数。
  - *影响维度*：主题审美 -1；专业度 -1。

- **渐变滥用**：页面上 `bg-gradient-to-*` 出现 5 次以上，头图、卡片、按钮、背景层层叠叠。
  - *取证*：`grep -rEn "bg-gradient-to-|from-[a-z]+-|via-[a-z]+-" src/ | wc -l` ≥ 5。
  - *影响维度*：视觉克制 -1；主题审美 -1。

## 2. 交互坏味道

- **重复提交不设防**：`onSubmit` 无 `disabled` / `isPending`，用户连点三次产生三条记录。
  - *取证*：搜表单组件 `onSubmit`，确认附近无 `disabled={isPending}` 或 `useTransition`；手动连点 3 次复现。
  - *影响维度*：健壮性 -2；交互完整度 -1。

- **loading 白屏**：数据接口未返回时页面空白，无 skeleton / spinner / 骨架屏。
  - *取证*：Network 面板里把接口 throttle 到 slow 3G，看 1–3 秒内页面有无任何占位；`grep -rn "Skeleton\|Spinner\|animate-pulse" src/`。
  - *影响维度*：加载体验 -2；感知性能 -1。

- **alert 式错误**：异常处理只有 `alert(err)` 或一闪而过的 toast，用户根本读不到。
  - *取证*：`grep -rEn "alert\(|window\.alert" src/`；`grep -rEn "toast\..*duration.*[0-9]{3,4}" src/` 看 duration 是否 < 1500。
  - *影响维度*：错误反馈 -2；专业度 -1。

- **空状态只有 "No data"**：列表为空时只有一行文字，无插画、无引导、无 CTA。
  - *取证*：清空数据复现空态；搜 `"No data"` / `"暂无数据"` 关键字，看周围是否有 `<EmptyState>` / 图标 / 按钮。
  - *影响维度*：空状态设计 -2；引导性 -1。

- **无 focus 环**：全局 `outline: none` 或未设置 `focus-visible`，键盘用户完全看不到焦点。
  - *取证*：`grep -rEn "outline-none|outline: *none" src/ app/`；Tab 键遍历页面，观察是否有可见焦点。
  - *影响维度*：可访问性 -2；键盘友好 -1。

- **点击零反馈**：按钮点下去 300ms 内没有 hover/active/loading 任何视觉变化。
  - *取证*：`grep -rEn "hover:|active:|disabled:" src/components/ui/`；逐个按钮点击录屏。
  - *影响维度*：交互反馈 -1；微交互 -1。

- **危险操作无二次确认**：删除、清空、发布等操作点一下就执行，无 Dialog / Confirm。
  - *取证*：搜 `onDelete` / `onRemove` / `destructive`，确认有无 `AlertDialog` / `confirm(` 包裹；手动点一次看是否直接生效。
  - *影响维度*：健壮性 -2；用户安全 -1。

- **提交后无反馈**：表单提交成功后既不清空、也不 toast、也不跳转，用户无法判断是否成功。
  - *取证*：提交一次表单，观察 DOM 是否有任何变化 / toast / reset；读 `onSubmit` 成功分支代码。
  - *影响维度*：交互完整度 -2；反馈闭环 -1。

## 3. 代码坏味道

- **巨型组件**：单个 `.tsx` 文件超过 500 行，混杂 UI、状态、请求、工具函数。
  - *取证*：`find src -name "*.tsx" -exec wc -l {} + | sort -rn | head -20`，≥ 500 行即命中。
  - *影响维度*：可维护性 -2；抽象合理性 -1。

- **TS 逃逸**：大量 `any` / `as unknown as X` / `// @ts-ignore`，类型系统形同虚设。
  - *取证*：`grep -rEn ": any\b|as any\b|as unknown as|@ts-ignore|@ts-nocheck" src/ | wc -l` ≥ 10。
  - *影响维度*：类型安全 -2；工程严谨 -1。

- **effect 依赖缺漏**：`useEffect` 没写依赖数组，或依赖漏写导致闭包捕获旧值。
  - *取证*：`grep -rEn "useEffect\s*\(" src/ -A 8 | grep -E "^\s*\}\)\s*$|^\s*\}, *\[" | head`；配合 ESLint `react-hooks/exhaustive-deps` 告警。
  - *影响维度*：正确性 -2；React 理解 -1。

- **裸 DOM 操作**：在 React 组件里用 `document.getElementById` / `document.querySelector` 改 DOM。
  - *取证*：`grep -rEn "document\.(getElementById|querySelector|querySelectorAll)" src/`。
  - *影响维度*：React 理解 -2；可测试性 -1。

- **prop drilling ≥ 3 层**：同一个 prop 被透传 3 层以上，没上 context / store。
  - *取证*：挑 2 个 prop 手工追踪引用链，确认传递层数；或看是否引入 zustand / context 但未使用。
  - *影响维度*：架构合理性 -2；可维护性 -1。

- **inline 大对象 prop**：每次渲染都新建对象 / 数组 / 函数作为 prop，破坏 `React.memo`。
  - *取证*：`grep -rEn "=\{\{.*:.*\}\}|=\{\[.*\]\}|=\{\(.*\)=>" src/components/ | head -30`，挑父组件看是否在 render 中新建。
  - *影响维度*：性能 -1；React 理解 -1。

- **单一超级 state**：所有字段塞一个 `useState(initialObject)` / `useReducer`，更新某一字段引发整体 re-render。
  - *取证*：搜 `useState\(\{[^}]{80,}` 或 `useReducer` 的 state 类型字段 ≥ 8 个；看是否拆分。
  - *影响维度*：状态管理 -2；性能 -1。

- **组件顶层发请求**：`fetch(...)` / `await` 直接写在函数组件主体，而非 `useEffect` / event handler / server component。
  - *取证*：`grep -rEn "^[^/]*await |^[^/]*fetch\(" src/components/ app/` 过滤出组件文件内非 effect / handler 的调用。
  - *影响维度*：React 理解 -2；正确性 -1。

## 4. 文案坏味道

- **按钮文案三件套**：`Submit` / `OK` / `Click here`，完全不说明操作内容。
  - *取证*：`grep -rEn ">(Submit|OK|Click here|点击|提交|确定)<" src/ app/`；人工看是否为关键 CTA。
  - *影响维度*：文案 -2；可用性 -1。

- **机翻错误信息**：报错文案像 Google Translate 直翻，或者直接把 `error.stack` 贴给用户。
  - *取证*：搜 `catch`/`onError` 附近文案；搜 `error\.stack|err\.stack|JSON\.stringify\(error` 是否直接渲染。
  - *影响维度*：文案 -2；安全性 -1（暴露实现）。

- **空状态文案干瘪**：`"No data"` / `"Nothing here"` / `"暂无"` 独自出现，没有上下文解释或下一步引导。
  - *取证*：搜关键字周围 50 字符，看是否有 CTA / 解释性说明。
  - *影响维度*：文案 -1；引导性 -1。

- **中英混用无规则**：同一页面 "Submit 成功" / "删除 failed"，无统一语言策略。
  - *取证*：抽 3 个页面，统计按钮 / toast / 标题的中英语言，若混杂且无 i18n 框架 → 命中。
  - *影响维度*：文案一致性 -2；专业度 -1。

- **错别字与时态混乱**：中文错别字（"登陆/登录" 混用）、英文时态错误（"Submited"）。
  - *取证*：人工读主要页面；搜常见错拼 `"登陆\|Submited\|Recieved\|Sucessful"`。
  - *影响维度*：文案 -1；专业度 -1。

- **占位文本未清理**：`Lorem ipsum` / `placeholder text` / `TODO` 留在页面里。
  - *取证*：`grep -rEn "[Ll]orem ipsum|placeholder text|TODO|FIXME|XXX" src/ app/`。
  - *影响维度*：完整度 -2；专业度 -1。
