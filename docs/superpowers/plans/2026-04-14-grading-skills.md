# Grading Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 交付两个评分 skill（前端 / 后端）+ 共享契约目录，供 Qoder/Cursor/Claude Code 在项目根 `skills/` 下使用。

**Architecture:** 扁平 Markdown 结构。两个 `SKILL.md` 内联全部评分流程、rubric、锚点、反模式、命令；`grading-shared/` 放 4 个契约文件（标尺、模板、JSON schema、证据规则）。

**Tech Stack:** Markdown + JSON Schema（draft-07）+ Bash/curl + `playwright-cli`（运行时命令，不是依赖）。

---

## 文件清单

| 文件 | 责任 |
|---|---|
| `skills/grading-shared/rubric-scale.md` | 0–10 分锚点 + S/A/B/C/D 档位，两个 skill 引用它作为打分标尺 |
| `skills/grading-shared/report-template.md` | Markdown 报告模板，所有评分产出严格按此格式 |
| `skills/grading-shared/score-schema.json` | JSON schema，用于班级 leaderboard 汇总 |
| `skills/grading-shared/evidence-requirements.md` | 证据硬约束（防幻觉） |
| `skills/grading-frontend/SKILL.md` | 前端评分入口：流程 + 10 维度 + 锚点 + 反模式 + 截图命令 |
| `skills/grading-backend/SKILL.md` | 后端评分入口：流程 + 9 维度 + 锚点 + 反模式 + probe 命令 |
| `scripts/validate-grading.sh` | 自检脚本：权重合计 + schema 验证（一次性，可丢） |

---

## 执行顺序

先做 `grading-shared/`（契约先定死），再并行做前后端两个 SKILL.md，最后跑自检脚本。

---

## Task 1：创建 `rubric-scale.md`

**Files:**
- Create: `skills/grading-shared/rubric-scale.md`

- [ ] **Step 1: 写文件**

内容：

````markdown
# 0–10 评分标尺

两个 grading skill 的**唯一打分依据**。评分时必须对照本文件给出的锚点，避免"凭感觉"打分。

## 单维度分数锚点

| 分数 | 含义 | 判定 |
|---:|---|---|
| **10** | 工业级范本，可作为教学样例 | 无可挑剔；可直接作为范本对外分享 |
| **9** | 优秀 | 1–2 处非关键瑕疵 |
| **7** | 良好 | 核心到位，但有多处可改进 |
| **5** | 及格 | 能用，但明显粗糙或有中度漏洞 |
| **3** | 不及格 | 有实现但很不完整 |
| **0** | 未实现 / 完全缺失 | |
| **N/A** | spec 未要求 | 不计入总分（从分母扣除权重） |

## 打分操作规则

1. **先选最接近的锚点**，再在上下 1 分内微调（禁止给 2/4/6/8 这种"中间保守分"之外的临时插值）
2. **N/A 必须在报告里写明原因**（哪条 spec 没要求），否则视为 0
3. **同一维度打分 ≥ 7 或 ≤ 4 时，必须至少 2 条证据**（见 evidence-requirements.md）

## 总分档位

| 档位 | 分数区间 | 释义 |
|---|---|---|
| **S** | ≥ 90 | 教学样例级 |
| **A** | 80–89 | 优秀 |
| **B** | 70–79 | 良好 |
| **C** | 60–69 | 及格 |
| **D** | < 60 | 未达标 |

## N/A 对总分的处理

```
total = Σ(score_i × weight_i) / Σ(weight_i for non-N/A dimensions) × 100
```

即：有 N/A 维度时从分母扣除其权重，保证总分仍在 0–100 区间。
````

- [ ] **Step 2: 自检**

跑：`wc -l skills/grading-shared/rubric-scale.md`
期望：文件存在，≥ 30 行。

- [ ] **Step 3: Commit**

```bash
git add skills/grading-shared/rubric-scale.md
git commit -m "feat(grading): add shared 0-10 rubric scale"
```

---

## Task 2：创建 `report-template.md`

**Files:**
- Create: `skills/grading-shared/report-template.md`

- [ ] **Step 1: 写文件**

内容：

````markdown
# 评分报告模板

两个 grading skill 输出的 `grading-report.md` 必须严格遵循此模板。

---

```markdown
# 项目评分报告 — {队伍名}（{前端|后端}）

- 评分人：{模型名或助教名}
- 日期：{YYYY-MM-DD}
- Spec 版本：{git sha 或 spec 文件名}
- 被评项目 commit：{sha}
- 评分耗时：{分钟}

## 总分：{score} / 100 — 等级 {S/A/B/C/D}

| 维度 | 得分 | 权重 | 加权 | 一句话评价 |
|---|---:|---:|---:|---|
| Spec 一致性 | 8 | 20 | 16.0 | 主流程对齐，遗漏管理员页面 |
| 主题与审美 | 6 | 12 | 7.2 | 配色偏默认，字体层级弱 |
| ... |
| **合计** | — | 100 | **78.4** | |

## 逐维度详评

### 1. Spec 一致性 — 8/10

**评分依据**
- 本次打 8 而非 10 的原因：spec §4.1 管理员审核页未实现

**证据**
- ✅ `src/pages/Dashboard.tsx:1-120` 实现 spec §3.2（列表页）
- ✅ `src/pages/Detail.tsx:1-80` 实现 spec §3.3（详情页）
- 📷 `.grading/shots/team-07-dashboard.png`
- ❌ 缺失：spec §4.1 的管理员审核页

**要到 10 差什么**
1. 补齐管理员审核页（spec §4.1）—— 包含列表 + 审批按钮 + 拒绝理由
2. 删除动作的二次确认弹窗缺失（spec §3.4.2）

---

（其余维度按同样模板）

## 亮点
- {一条}
- {一条}

## 最该优先修的 3 件事
1. {最影响分数的一项}
2. {第二}
3. {第三}
```
````

- [ ] **Step 2: Commit**

```bash
git add skills/grading-shared/report-template.md
git commit -m "feat(grading): add shared report template"
```

---

## Task 3：创建 `score-schema.json` + 写 sample 并验证

**Files:**
- Create: `skills/grading-shared/score-schema.json`
- Create: `scripts/validate-grading.sh`（临时，后面所有任务会复用）

- [ ] **Step 1: 写 schema**

内容：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GradingSummary",
  "type": "object",
  "required": ["team", "side", "total", "grade", "dimensions", "graded_at"],
  "properties": {
    "team": { "type": "string" },
    "side": { "enum": ["frontend", "backend"] },
    "total": { "type": "number", "minimum": 0, "maximum": 100 },
    "grade": { "enum": ["S", "A", "B", "C", "D"] },
    "dimensions": {
      "type": "array",
      "minItems": 9,
      "items": {
        "type": "object",
        "required": ["name", "weight"],
        "properties": {
          "name": { "type": "string" },
          "score": { "type": ["number", "null"], "minimum": 0, "maximum": 10 },
          "weight": { "type": "number", "minimum": 0, "maximum": 100 },
          "weighted": { "type": "number" },
          "na_reason": { "type": "string" }
        }
      }
    },
    "top_fixes": {
      "type": "array",
      "items": { "type": "string" },
      "maxItems": 5
    },
    "evidence_count": { "type": "integer", "minimum": 0 },
    "spec_sha": { "type": "string" },
    "project_sha": { "type": "string" },
    "graded_at": { "type": "string", "format": "date-time" }
  }
}
```

- [ ] **Step 2: 写自检脚本**

写 `scripts/validate-grading.sh`：

```bash
#!/usr/bin/env bash
set -e

cd "$(git rev-parse --show-toplevel)"

echo "=== 1. 验证 score-schema.json 本身合法 ==="
node -e "JSON.parse(require('fs').readFileSync('skills/grading-shared/score-schema.json','utf8'))"

echo "=== 2. 构造 sample summary 并验证通过 schema ==="
cat > /tmp/sample-summary.json <<'EOF'
{
  "team": "team-07",
  "side": "frontend",
  "total": 78.4,
  "grade": "B",
  "dimensions": [
    {"name":"spec-conformance","score":8,"weight":20,"weighted":16.0},
    {"name":"theme-aesthetic","score":6,"weight":12,"weighted":7.2},
    {"name":"animation","score":7,"weight":10,"weighted":7.0},
    {"name":"state-completeness","score":8,"weight":10,"weighted":8.0},
    {"name":"code-quality","score":7,"weight":10,"weighted":7.0},
    {"name":"responsive","score":8,"weight":8,"weighted":6.4},
    {"name":"forms","score":9,"weight":8,"weighted":7.2},
    {"name":"performance","score":8,"weight":8,"weighted":6.4},
    {"name":"a11y","score":5,"weight":8,"weighted":4.0},
    {"name":"microcopy","score":8,"weight":6,"weighted":4.8}
  ],
  "top_fixes": ["补管理员页","加 error boundary","统一按钮 hover"],
  "evidence_count": 23,
  "graded_at": "2026-04-14T10:00:00Z"
}
EOF

npx --yes ajv-cli validate \
  -s skills/grading-shared/score-schema.json \
  -d /tmp/sample-summary.json

echo "=== 3. 验证前端权重合计 = 100 ==="
node -e '
const fs = require("fs");
const s = JSON.parse(fs.readFileSync("/tmp/sample-summary.json","utf8"));
const sum = s.dimensions.reduce((a,d)=>a+d.weight,0);
if (sum !== 100) { console.error("weight sum =", sum, "expected 100"); process.exit(1); }
console.log("weight sum OK (100)");
'

echo "=== ALL OK ==="
```

- [ ] **Step 3: 跑自检脚本**

Run:
```bash
chmod +x scripts/validate-grading.sh && ./scripts/validate-grading.sh
```
期望输出：`=== ALL OK ===`。

- [ ] **Step 4: Commit**

```bash
git add skills/grading-shared/score-schema.json scripts/validate-grading.sh
git commit -m "feat(grading): add score schema + validate script"
```

---

## Task 4：创建 `evidence-requirements.md`

**Files:**
- Create: `skills/grading-shared/evidence-requirements.md`

- [ ] **Step 1: 写文件**

内容：

````markdown
# 证据硬约束

防止 Claude/Cursor agent 拍脑袋打分的核心防线。**两个 grading skill 都必须遵守。**

## 规则

| 打分 | 最少证据条数 |
|---:|---:|
| 9–10 | 3 条 |
| 7–8 | 2 条 |
| 5–6 | 1 条 |
| 3–4 | 2 条（证明确实差） |
| 0 | 1 条（证明确实不存在） |
| N/A | 1 条（spec 原文引用） |

## 证据的合法形式

- **代码引用**：`src/xxx.tsx:12-40` 格式（必须是文件:行号，不能只是文件名）
- **截图**：`.grading/shots/<team>-<view>.png`
- **命令日志**：`.grading/probes/<team>-<probe>.log`，包含实际执行的命令和输出
- **Spec 引用**：`spec §x.y` 或 spec 文件的 markdown 行号

## 违规处理

打分 ≥ 7 或 ≤ 4 但证据数不足时，skill 必须：
1. 把该维度的 score 置为 `null`
2. 在 `na_reason` 写 `"EVIDENCE_MISSING: 需要补 N 条证据"`
3. 在报告底部 `## 评分风险` 段列出所有 EVIDENCE_MISSING 的维度

**此规则优先于任何"评分完毕"的判断**：有风险的报告不能直接出具 S/A/B/C/D 档位。
````

- [ ] **Step 2: Commit**

```bash
git add skills/grading-shared/evidence-requirements.md
git commit -m "feat(grading): add evidence requirements (anti-hallucination)"
```

---

## Task 5：创建 `grading-frontend/SKILL.md`

**Files:**
- Create: `skills/grading-frontend/SKILL.md`

- [ ] **Step 1: 写文件（骨架 + 10 维度）**

SKILL.md 结构：

````markdown
---
name: grading-frontend
description: Grade a team's frontend implementation against its spec on 10 weighted dimensions, producing a markdown report + JSON summary with evidence.
---

# grading-frontend

给 4 人小队交付的前端项目打分。输出一份给学员看的 Markdown 报告和一份给助教汇总用的 JSON。

**使用场景**：讲师/助教指着某个小队的仓库说"评一下前端"。

## 前置依赖

- 被评项目可本地跑起来（`npm run dev` 等）
- spec 文档位置已知（通常是 `spec/` 或 `docs/spec.md`）
- 有 Node.js 环境（用于 `npx playwright-cli` 和 `ajv-cli`）

## 共享契约（必读）

评分前必须阅读：
- `../grading-shared/rubric-scale.md` — 0–10 分锚点
- `../grading-shared/report-template.md` — 报告格式
- `../grading-shared/evidence-requirements.md` — 证据硬约束
- `../grading-shared/score-schema.json` — JSON schema

## 评分流程

### 步骤 1：定位与启动

```bash
# 准备产出目录
mkdir -p .grading/{shots,probes,reports}

# 识别技术栈
cat <project>/package.json | jq '.dependencies + .devDependencies | keys'

# 起前端
cd <project> && npm install && npm run dev  # 后台执行，记下端口
```

### 步骤 2：收集证据

用 playwright-cli 截图 4 个关键视图 + 1 个移动端：

```bash
# 安装（一次性）
npx playwright install chromium

TEAM=team-07
BASE=http://localhost:3000

for view in "" login dashboard detail empty error; do
  path=${view:-index}
  npx playwright-cli screenshot --viewport-size=1280,800 \
    $BASE/$view .grading/shots/$TEAM-desktop-$path.png
done

npx playwright-cli screenshot --viewport-size=375,812 \
  $BASE .grading/shots/$TEAM-mobile.png
```

手动过一遍关键交互（登录/提交/删除），记录：
- 过程中的 console 错误
- 接口失败时的 UX
- 加载态有没有 skeleton

### 步骤 3：按 10 维度逐条打分

每个维度必须：
1. 找锚点（参照 rubric-scale.md）
2. 收集证据（参照 evidence-requirements.md）
3. 写"要到 10 差什么"

### 步骤 4：产出两份文件

- `.grading/reports/<team>-frontend.md` — 遵循 report-template.md
- `.grading/reports/<team>-frontend.json` — 遵循 score-schema.json

### 步骤 5：自检

```bash
./scripts/validate-grading.sh  # 仓库里有的话
# 或手动跑 ajv-cli 验证 JSON
npx --yes ajv-cli validate \
  -s skills/grading-shared/score-schema.json \
  -d .grading/reports/<team>-frontend.json
```

---

## 10 个评分维度

### 1. Spec 一致性（权重 20）

**关注点**
- spec 里列的页面是否都实现
- 字段、交互、流程是否对齐（不是"看起来差不多"）
- 有没有超纲的自由发挥（加分 vs 扣分）

**锚点**
- 10：所有 spec 页面 + 交互 + 字段 100% 对齐，超纲都是明显增值
- 7：主流程对齐，遗漏 1 个次要页面或几个字段
- 5：核心 1–2 个页面能跑，其他缺失或与 spec 偏离明显
- 3：基本没按 spec 来，自创一套
- 0：完全看不出与 spec 的对应

**取证方法**
1. 逐条过 spec 的页面清单，打勾或打叉
2. 针对关键字段查源码 `grep -r "<field-name>" src/`
3. 对比 spec 约定的交互步骤和实际点击路径

**证据要求**
- 至少 3 条 file:line 引用 + 2 张截图

---

### 2. 主题与审美（权重 12）

**关注点**
- 配色：是否有主题色而不是"灰灰白白"默认
- 字体：字号层级、行高是否舒适
- 间距/圆角/阴影：是否一致
- 有没有典型 AI slop 味

**锚点**
- 10：有明确主题色系统，字体层级清晰，视觉一致度接近高端 SaaS
- 7：有主题色但层级略混乱；或字体完美但配色偏默认
- 5：默认 shadcn/Tailwind 感明显，无定制
- 3：颜色混乱（十种灰），无统一风格

**AI slop 反模式清单**（出现任一扣 2 分）
- 全局只有 `gray-100/200/...` 灰灰白白
- 默认 shadcn 未改主题色
- 所有卡片同 `rounded-lg shadow`
- 按钮都是 `bg-blue-500 hover:bg-blue-600`
- 空状态只有 "No data"

**取证方法**
1. 截图对比配色与字体层级
2. grep `bg-gray` / `text-gray` 占总色类的比例
3. 找 `tailwind.config.{js,ts}` 看有没有自定义 theme

---

### 3. 动画与流畅度（权重 10）

**关注点**
- 页面切换 / 模态出现 / 列表增删的过渡
- 微交互（按钮 hover、input focus、checkbox 切换）
- 有无明显卡顿 / layout shift

**锚点**
- 10：关键交互都有恰到好处的过渡，60fps 无卡顿，无 layout shift
- 7：主要过渡都有但 1–2 处生硬
- 5：只有默认 Tailwind transition，无刻意设计
- 3：很多地方"闪现"，无过渡
- 0：有明显 layout shift / 掉帧

**取证方法**
1. 录屏（或描述）关键过渡
2. DevTools Performance 看有无长任务

---

### 4. 状态完备性（权重 10）

**关注点**：loading / empty / error / success 四态是否都处理。

**锚点**
- 10：四态全覆盖，empty 有 CTA，error 有重试，loading 有 skeleton
- 7：三态齐全，缺一个
- 5：只做 loading + success
- 3：只有 happy path

**取证方法**
1. 断网看 error 态
2. 清空数据看 empty 态
3. 节流 3G 看 loading 态

**证据要求**：四态各一张截图（如 N/A 则 spec 引用）

---

### 5. 代码质量（权重 10）

**关注点**
- 组件拆分：单文件 LOC 是否失控（> 300 行警告）
- TS 类型：是否大量 `any` / `as unknown as`
- Hooks 正确性：有无 useEffect 依赖缺失
- Prop drilling：是否该用 context/状态管理

**锚点**
- 10：结构清晰、类型严格、无明显坏味道
- 7：基本良好，2–3 处可改进
- 5：有几个大文件或多处 `any`
- 3：组件杂糅 + 大量 `any`

**取证方法**
1. `wc -l src/**/*.tsx | sort -n | tail`
2. `grep -rn "as any\|: any" src/ | wc -l`
3. 抽查 3 个大组件

---

### 6. 响应式适配（权重 8）

**锚点**
- 10：mobile/tablet/desktop 三档都有针对性设计
- 7：手机适配但平板等于桌面
- 5：只在桌面看着 OK
- 3：手机上元素溢出、按钮点不到

**取证方法**
用 playwright-cli 375/768/1280 三档各截一张图。

---

### 7. 表单与输入反馈（权重 8）

**关注点**
- 必填/格式校验有无实时提示
- 提交中按钮是否禁用（防重复提交）
- 失败的错误信息是否人话

**锚点**
- 10：实时校验 + 防重复 + 人话错误 + 提交成功反馈
- 7：有校验但错误信息不够友好
- 5：只有 HTML 原生校验
- 3：无校验 / 错误直接弹 500 堆栈

---

### 8. 性能（权重 8）

**关注点**
- 首屏时间
- 交互响应（点击 → 视觉反馈 < 100ms）
- bundle size

**取证方法**
```bash
npx --yes lighthouse http://localhost:3000 \
  --only-categories=performance --quiet \
  --output json --output-path .grading/probes/<team>-lighthouse.json
cat .grading/probes/<team>-lighthouse.json | jq '.categories.performance.score'
```

**锚点**：Lighthouse Performance score
- 10：≥ 0.9
- 7：≥ 0.7
- 5：≥ 0.5
- 3：< 0.5

---

### 9. 无障碍 (a11y)（权重 8）

**关注点**
- 键盘能否走完主流程（Tab + Enter）
- focus-visible 环是否存在
- 对比度是否够（文字 ≥ 4.5:1）
- 语义化 HTML / ARIA

**锚点**
- 10：键盘完全可达 + focus 清晰 + axe 无严重问题
- 7：基本可达但有死角
- 5：有 focus 环但键盘不能走完
- 3：鼠标 only

**取证方法**
```bash
# axe CLI
npx --yes @axe-core/cli http://localhost:3000 \
  --save .grading/probes/<team>-axe.json
```

---

### 10. 微文案（权重 6）

**关注点**
- 按钮文案是否动作具体（"保存更改" vs "提交"）
- 空状态是否有引导 CTA
- 错误信息是否告诉用户下一步

**锚点**
- 10：所有文案贴合场景，有温度
- 7：核心文案到位，零散处有 "Submit"/"No data"
- 5：大量默认英文短词
- 3：文案机翻感强 / 错别字

---

## 反模式快查表（打分时随时对照）

### AI slop（视觉）
- 全灰灰白白
- 默认 shadcn 未改色
- 卡片千篇一律 `rounded-lg shadow`

### 代码坏味道
- 单组件 > 500 行
- 大量 `any` / `as unknown as`
- useEffect 无依赖数组
- 直接操作 DOM（`document.getElementById`）

### 交互坏味道
- 接口未返回就允许再次提交
- 错误 toast 停 1 秒就消失
- loading 状态是空白屏

---

## 产出 checklist

- [ ] `.grading/reports/<team>-frontend.md` 按 report-template.md 格式
- [ ] `.grading/reports/<team>-frontend.json` 通过 ajv 验证
- [ ] 每维度打分 ≥ 7 或 ≤ 4 都有 ≥ 2 条证据
- [ ] 无 EVIDENCE_MISSING 维度，或已在"评分风险"段列明
````

- [ ] **Step 2: 验证文件结构**

Run:
```bash
grep -c "^### [0-9]" skills/grading-frontend/SKILL.md
```
Expected: `10`（10 个维度标题）

- [ ] **Step 3: 验证权重合计 = 100**

Run:
```bash
grep -oE "权重 [0-9]+" skills/grading-frontend/SKILL.md | awk '{s+=$2} END {print s}'
```
Expected: `100`

- [ ] **Step 4: Commit**

```bash
git add skills/grading-frontend/SKILL.md
git commit -m "feat(grading-frontend): add skill with 10 weighted dimensions"
```

---

## Task 6：创建 `grading-backend/SKILL.md`

**Files:**
- Create: `skills/grading-backend/SKILL.md`

- [ ] **Step 1: 写文件（骨架 + 9 维度）**

结构与前端相似，替换为后端 9 维度。关键差异点：

````markdown
---
name: grading-backend
description: Grade a team's backend implementation against its spec on 9 weighted dimensions, producing a markdown report + JSON summary with evidence.
---

# grading-backend

## 评分流程

### 步骤 1：定位与启动

```bash
mkdir -p .grading/{probes,reports}

# 识别技术栈
ls <project>/{package.json,pyproject.toml,go.mod,pom.xml,Cargo.toml} 2>/dev/null

# 起服务（按栈）
cd <project> && <启动命令> &  # 后台
# 等健康检查通过
until curl -sf localhost:8080/health; do sleep 1; done
```

### 步骤 2：收集证据

对每个 spec §x 的接口，按清单跑 probe：

```bash
BASE=http://localhost:8080
TEAM=team-07

# 健壮性探针
curl -s -o .grading/probes/$TEAM-empty-body.log -w "%{http_code}" \
  -X POST $BASE/api/items -H 'Content-Type: application/json' -d '{}'

curl -s -o .grading/probes/$TEAM-malformed-json.log -w "%{http_code}" \
  -X POST $BASE/api/items -H 'Content-Type: application/json' -d 'not json'

# 超长字段
curl -s -o .grading/probes/$TEAM-oversize.log -w "%{http_code}" \
  -X POST $BASE/api/items -H 'Content-Type: application/json' \
  -d "{\"name\":\"$(printf 'A%.0s' {1..10000})\"}"

# 幂等性：两次相同请求
for i in 1 2; do
  curl -s -o .grading/probes/$TEAM-idem-$i.log \
    -X POST $BASE/api/items -H 'X-Request-Id: same-id' \
    -H 'Content-Type: application/json' -d '{"name":"test"}'
done

# 并发
seq 10 | xargs -P 10 -I{} curl -s -o /dev/null -w "%{http_code}\n" \
  $BASE/api/items > .grading/probes/$TEAM-concurrent.log

# 性能（可选）
npx --yes autocannon -d 5 -c 10 $BASE/api/items \
  > .grading/probes/$TEAM-autocannon.log 2>&1
```

### 步骤 3：跑测试套件

```bash
# Node
cd <project> && npm test -- --coverage > .grading/probes/$TEAM-test.log 2>&1
# Python
pytest --cov > .grading/probes/$TEAM-test.log 2>&1
# Go
go test -cover ./... > .grading/probes/$TEAM-test.log 2>&1
```

---

## 9 个评分维度

### 1. Spec 一致性（权重 20）
同前端：逐条对 spec §x 的接口/字段/状态码。证据含 curl + 响应 + file:line。

### 2. 健壮性（权重 15）

**锚点**
- 10：所有 probe 返回合理状态码（4xx 不是 500）；幂等键生效；并发无脏数据
- 7：主路径健壮，边界 1–2 处疏漏（如超长字段报 500）
- 5：Happy path OK，异常普遍 500
- 3：抛堆栈到前端

**必看 probe**：empty-body / malformed-json / oversize / idem / concurrent

### 3. API 设计（权重 12）
- 状态码用对（POST 创建返 201）
- 错误响应格式统一
- 分页/过滤/排序参数规范
- 资源命名 RESTful

### 4. 测试（权重 12）
**锚点**
- 10：覆盖率 ≥ 70% + 关键路径有测试 + 真能跑通
- 7：覆盖率 ≥ 50%
- 5：有测试但只覆盖 happy path
- 3：几乎没测试或根本跑不通

### 5. 数据建模（权重 10）
- schema 合理（类型、约束、外键）
- 有索引（尤其外键和常查询字段）
- migration 脚本可重放

```bash
# 检查有无 migrations
ls <project>/{migrations,prisma/migrations,alembic/versions} 2>/dev/null
```

### 6. 代码分层（权重 10）
- controller / service / repo 有清晰边界
- 业务逻辑不漏到 controller
- 数据库调用不漏到 controller

**坏味道扫描**
```bash
# controller 里直接 SQL / ORM 调用
grep -rn "db\.\|prisma\.\|sqlalchemy" <project>/controllers/ 2>/dev/null
```

### 7. 性能（权重 8）
- p50 / p95 接口耗时
- 无 N+1 查询
- SQL 有用到索引

### 8. 可观测性（权重 7）
- 结构化日志（非 `console.log` / `print`）
- 关键操作（登录、写入、错误）都有日志
- 错误日志含上下文（request id、user id）

### 9. 文档（权重 6）
- README 能 5 分钟跑起来
- 接口文档存在（Swagger/Postman/Markdown）
- 示例 curl 能直接跑通

---

## 反模式快查表

- 控制器里 10 行 SQL
- `try: ... except: pass` 吞异常
- N+1：`for x in xs: db.query(x.id)`
- 错误响应每个接口都不一样
- 写操作不幂等
- 日志只有 `print`
- 直接把 ORM 异常 str 化返给前端

---

## 产出 checklist

- [ ] `.grading/reports/<team>-backend.md` 按 report-template.md 格式
- [ ] `.grading/reports/<team>-backend.json` 通过 ajv 验证
- [ ] 每维度证据满足 evidence-requirements.md
- [ ] 至少 5 个 probe 日志归档到 `.grading/probes/`
````

- [ ] **Step 2: 验证维度数**

Run:
```bash
grep -c "^### [0-9]" skills/grading-backend/SKILL.md
```
Expected: `9`

- [ ] **Step 3: 验证权重合计 = 100**

Run:
```bash
grep -oE "权重 [0-9]+" skills/grading-backend/SKILL.md | awk '{s+=$2} END {print s}'
```
Expected: `100`

- [ ] **Step 4: Commit**

```bash
git add skills/grading-backend/SKILL.md
git commit -m "feat(grading-backend): add skill with 9 weighted dimensions"
```

---

## Task 7：端到端 dry-run + 自检

**Files:**
- Extend: `scripts/validate-grading.sh`

- [ ] **Step 1: 扩充自检脚本**

在原 `scripts/validate-grading.sh` 底部追加：

```bash
echo "=== 4. 验证前端 SKILL.md 10 维度 权重=100 ==="
cnt=$(grep -c "^### [0-9]" skills/grading-frontend/SKILL.md)
[ "$cnt" = "10" ] || { echo "frontend dimensions $cnt != 10"; exit 1; }
sum=$(grep -oE "权重 [0-9]+" skills/grading-frontend/SKILL.md | awk '{s+=$2} END {print s}')
[ "$sum" = "100" ] || { echo "frontend weight sum $sum != 100"; exit 1; }

echo "=== 5. 验证后端 SKILL.md 9 维度 权重=100 ==="
cnt=$(grep -c "^### [0-9]" skills/grading-backend/SKILL.md)
[ "$cnt" = "9" ] || { echo "backend dimensions $cnt != 9"; exit 1; }
sum=$(grep -oE "权重 [0-9]+" skills/grading-backend/SKILL.md | awk '{s+=$2} END {print s}')
[ "$sum" = "100" ] || { echo "backend weight sum $sum != 100"; exit 1; }

echo "=== 6. 验证 shared/ 四文件齐全 ==="
for f in rubric-scale.md report-template.md score-schema.json evidence-requirements.md; do
  [ -f "skills/grading-shared/$f" ] || { echo "missing skills/grading-shared/$f"; exit 1; }
done

echo "=== ALL OK ==="
```

- [ ] **Step 2: 跑完整自检**

Run:
```bash
./scripts/validate-grading.sh
```
Expected: 全部通过，最后一行 `=== ALL OK ===`。

- [ ] **Step 3: 手工挑一个小队做 dry-run**

选 `group-workshop/group-1`，让评分 agent 执行 `skills/grading-frontend/SKILL.md`，产出：
- `.grading/reports/group-1-frontend.md`
- `.grading/reports/group-1-frontend.json`

验证：
```bash
npx --yes ajv-cli validate \
  -s skills/grading-shared/score-schema.json \
  -d .grading/reports/group-1-frontend.json
```

- [ ] **Step 4: 根据 dry-run 反馈微调**

- 如果 agent 在某维度频繁给 EVIDENCE_MISSING，在 SKILL.md 的"取证方法"里补更具体的命令
- 如果 agent 打分分布过集中（全都 5–7），在 rubric-scale.md 的锚点里加反例

- [ ] **Step 5: Commit**

```bash
git add scripts/validate-grading.sh
git add .gitignore  # 如果要把 .grading/ 加入
git commit -m "feat(grading): add end-to-end validation + dry-run fixes"
```

---

## Self-Review Checklist（执行前过一遍）

- [ ] 7 个文件全部在清单里，每个都有独立 Task
- [ ] `scripts/validate-grading.sh` 的 6 步自检覆盖：JSON schema 合法 / sample 通过 / 前后端维度数 / 前后端权重合计 / shared 文件齐全
- [ ] 前端 10 维度权重：20+12+10+10+10+8+8+8+8+6 = 100 ✓
- [ ] 后端 9 维度权重：20+15+12+12+10+10+8+7+6 = 100 ✓
- [ ] 每个 SKILL.md 都引用了 4 个 shared 契约文件
- [ ] 截图命令用的是 `playwright-cli`（符合方案 A）
- [ ] 所有 Bash 命令都是可直接粘贴执行的，无 placeholder
