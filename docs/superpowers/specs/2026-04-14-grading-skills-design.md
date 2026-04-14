# Grading Skills Design — Frontend & Backend

**Date**: 2026-04-14
**Author**: Jake (via brainstorming with Claude)
**Status**: Approved — ready for implementation plan

---

## 1. Context & Goals

### Context

- 培训项目：50 名学员，~12 个 4 人小队，按 **Spec-driven** 方式实现一个前后端网站
- 部署目标：**本地**（不是生产）
- 评分场景：讲师/助教对每个项目出"工业级"评价，既要给学员可操作反馈，也要能横向对比

### Goals

1. 两个独立但共享规则的 skill：`grading-frontend` 和 `grading-backend`
2. 输出一致、可汇总成班级 leaderboard
3. 每个维度既有分数又有"要到 10 分差什么"的教学反馈
4. 证据先行，防止 Claude 拍脑袋打分

### Non-Goals（本地培训项目不考虑）

- 前端：SEO / Metadata、安全（XSS/CSP 等）、前端工程化（lint/CI/env）
- 后端：部署与配置、CI/CD、供应链安全
- 跨项目：Git / 协作痕迹、README 上手成本

---

## 2. Architecture

**目标 IDE**：Qoder（主要）、兼容 Cursor / Antigravity / Claude Code。共同点都是 Markdown-based skill。
**安装位置**：项目根目录下的 `skills/`（即 `group-workshop/skills/`），随仓库版本管理。
**截图方案**：评分流程里的截图通过 `npx playwright-cli` 命令完成，skill 里内置命令；agent 自己执行，无需 MCP。

**简化原则**（基于"当前设计太复杂"反馈）：
- 砍掉 `references/`、`examples/`、`calibration/` 三个子目录
- 将精华（锚点、反模式、取证命令）全部内联进 `SKILL.md`
- 每个 skill 实际只有 1 个核心文件 + 可选 1 个辅助文件
- `grading-shared/` 保留 4 个薄文件作为契约（标尺、模板、schema、证据规则）

```
group-workshop/
└── skills/
    ├── grading-frontend/
    │   └── SKILL.md                     # 流程 + 10 维度 rubric + 锚点 + 反模式 + 截图命令
    ├── grading-backend/
    │   └── SKILL.md                     # 流程 + 9 维度 rubric + 锚点 + 反模式 + probe 命令
    └── grading-shared/
        ├── rubric-scale.md              # 0–10 标尺（两 skill 都引用此文件）
        ├── report-template.md           # 统一 Markdown 报告模板
        ├── score-schema.json            # JSON 汇总 schema
        └── evidence-requirements.md     # 每分项证据硬约束
```

评分运行时产出（被 gitignore）：

```
.grading/
├── shots/<team>-<view>.png              # playwright-cli 截图
├── probes/<team>-<probe>.log            # curl / 压测输出
└── reports/<team>-<side>.{md,json}      # 最终报告
```

### 为什么是这个结构（vs. 单一 skill 带 mode）

- 单一职责：每个 skill 只管一侧，阅读和维护更清爽
- 维度独立：前端 10 维 vs 后端 9 维，权重也不一样，塞一起很乱
- 共享 shared/：保证 0–10 标尺、报告模板、JSON schema 绝对一致，班级 leaderboard 才可比

---

## 3. 运行时流程（两个 skill 共用框架）

```
1. 定位项目
   - 读 spec 文档（docs/spec.md / README / spec/*）
   - 识别技术栈（package.json / pyproject.toml / go.mod ...）

2. 收集证据（evidence-first）
   前端：
     - 静态：扫组件树、路由、CSS/Tailwind、TS 类型、状态管理
     - 动态：启动 dev server → 过关键页面 → 截图 → 检查 console/network
     - 交互：跑主流程（登录/提交/列表等）
   后端：
     - 静态：接口清单 vs spec、分层结构、schema/迁移、测试目录
     - 动态：起服务 → 按 spec 打关键接口 → 看响应码/耗时/错误处理
     - 测试：跑 test suite，看覆盖率与结果

3. 按维度逐条打分（0–10）
   - 每维度必须引用证据（file:line / 截图路径 / curl 命令）
   - 未覆盖项写 "N/A — 原因"，不计入总分

4. 写"要到 10 差什么"
   - 为每个维度列 2–4 条具体改进建议

5. 产出两个文件
   - grading-report.md   （人类可读，给学员）
   - grading-summary.json （给助教汇总 leaderboard）
```

---

## 4. 0–10 标尺（`grading-shared/rubric-scale.md`）

| 分数 | 含义 |
|---|---|
| **10** | 工业级范本，可作为教学样例 |
| **9** | 优秀，1–2 处非关键瑕疵 |
| **7** | 良好，核心到位但多处可改进 |
| **5** | 及格，能用但明显粗糙或漏洞 |
| **3** | 不及格，有 1 项但很不完整 |
| **0** | 未实现 / 完全缺失 |
| **N/A** | spec 未要求，不计入总分 |

**总分档位**
- S (≥ 90)
- A (80–89)
- B (70–79)
- C (60–69)
- D (< 60)

---

## 5. 前端维度与权重（总 100）

| # | 维度 | 权重 | 关注点 |
|---|---|---:|---|
| 1 | Spec 一致性 | 20 | 页面/组件/流程是否与 spec 对齐；有无偷工减料或超纲 |
| 2 | 主题与审美 | 12 | 配色、字体、间距、视觉一致性；有无 AI slop 味 |
| 3 | 动画与流畅度 | 10 | 过渡自然度、微交互、60fps、无 layout shift |
| 4 | 状态完备性 | 10 | loading / empty / error / success 四态 |
| 5 | 代码质量 | 10 | 组件拆分、TS 类型、hooks 正确、无 prop drilling |
| 6 | 响应式适配 | 8 | mobile / tablet / desktop 断点 |
| 7 | 表单与输入反馈 | 8 | 校验、错误提示、禁用态、防重复提交 |
| 8 | 性能 | 8 | 首屏、交互响应、bundle 合理 |
| 9 | 无障碍 (a11y) | 8 | 键盘导航、语义化、对比度 |
| 10 | 微文案 | 6 | 按钮/空态/错误信息的专业度 |

---

## 6. 后端维度与权重（总 100）

| # | 维度 | 权重 | 关注点 |
|---|---|---:|---|
| 1 | Spec 一致性 | 20 | API 契约、字段、状态码是否匹配 spec |
| 2 | 健壮性 | 15 | 错误处理、边界、幂等、并发安全 |
| 3 | API 设计 | 12 | RESTful、状态码、错误码统一、分页/过滤 |
| 4 | 测试 | 12 | 覆盖率、关键路径、是否真跑通 |
| 5 | 数据建模 | 10 | schema、索引、外键、迁移脚本 |
| 6 | 代码分层 | 10 | controller/service/repo 清晰、无逻辑泄漏 |
| 7 | 性能 | 8 | 接口耗时、SQL 效率、无 N+1 |
| 8 | 可观测性 | 7 | 结构化日志、关键操作有迹可循 |
| 9 | 文档 | 6 | README、接口文档、示例可跑通 |

---

## 7. Rubric 细则模板

每个维度在 SKILL.md 中采用统一格式，示例（后端"健壮性"）：

```markdown
### 维度 2：健壮性 (权重 15)

**评分关注点**
- 所有异常路径是否被处理（不是 try/catch 吞错）
- 输入是否校验（类型、范围、必填）
- 关键写操作是否幂等（重试不重复创建）
- 并发冲突是否考虑（乐观锁 / 事务）

**锚点**
- 10：所有接口过混沌输入测试；关键写操作幂等；有明确错误码体系
- 7 ：主路径健壮，但边界/并发有 1–2 处疏漏
- 5 ：Happy path 能跑，异常路径多处直接 500
- 3 ：基本没做异常处理，或报错直接把堆栈抛给前端

**取证方法**
1. 跑 probe：空 body / 错误类型 / 超长字段 / 重复提交 / 并发同一资源
2. 检查响应码与错误信息格式
3. grep try/except 看是否有吞错

**证据要求**
- 至少 3 个 probe 的 curl + 响应
- 至少 2 个 file:line 引用
```

前端 10 个 + 后端 9 个 = 19 个 rubric 块。

---

## 8. 完整目录结构（简化版）

```
skills/
├── grading-frontend/
│   └── SKILL.md           # 流程 + 10 维度 rubric + 锚点 + AI slop 反模式 + 截图命令
├── grading-backend/
│   └── SKILL.md           # 流程 + 9 维度 rubric + 锚点 + 反模式 + probe 命令
└── grading-shared/
    ├── rubric-scale.md            # 0–10 标尺 + S/A/B/C/D 档位
    ├── report-template.md         # 统一 Markdown 报告模板
    ├── score-schema.json          # JSON 汇总 schema（用于班级 leaderboard）
    └── evidence-requirements.md   # 每分项证据硬约束
```

### 截图命令（内联在 grading-frontend/SKILL.md 中）

```bash
# 一次性安装
npx playwright install chromium

# 截单页
npx playwright-cli screenshot --viewport-size=1280,800 \
  http://localhost:3000/login .grading/shots/<team>-login.png

# 截四态（成功/空/加载/错误）—— agent 按路由循环
for view in login dashboard empty error; do
  npx playwright-cli screenshot --viewport-size=1280,800 \
    http://localhost:3000/$view .grading/shots/<team>-$view.png
done

# 移动端断点
npx playwright-cli screenshot --viewport-size=375,812 \
  http://localhost:3000 .grading/shots/<team>-mobile.png
```

如果 `playwright-cli` 不可用，fallback 提示评分人手动放置截图到 `.grading/shots/`。

### 后端 probe 命令（内联在 grading-backend/SKILL.md 中）

```bash
# 健壮性：空 body
curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8080/api/items \
  -H "Content-Type: application/json" -d '{}'

# 健壮性：超长字段
curl -s -X POST localhost:8080/api/items \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$(printf 'A%.0s' {1..10000})\"}"

# 幂等性：同一请求打两次看是否产生两条记录
curl -s -X POST localhost:8080/api/items -d @payload.json
curl -s -X POST localhost:8080/api/items -d @payload.json

# 性能：autocannon 压测（可选）
npx autocannon -d 5 -c 10 http://localhost:8080/api/items
```

---

## 9. 报告模板（`grading-shared/report-template.md`）

````markdown
# 项目评分报告 — {队伍名}（{前端|后端}）

评分人：{Claude@sonnet-4.6 / 助教XX}
日期：{YYYY-MM-DD}
Spec 版本：{git sha / 文件名}
被评项目 commit：{sha}

## 总分：{score} / 100 — 等级 {S/A/B/C/D}

| 维度 | 得分 | 权重 | 加权 | 一句话 |
|---|---:|---:|---:|---|
| Spec 一致性 | 8 | 20 | 16.0 | 主流程对齐，遗漏管理员页面 |
| ... |

## 逐维度详评

### 1. Spec 一致性 — 8/10

**证据**
- `src/pages/Dashboard.tsx:1-120` 实现 spec §3.2
- 截图：`.grading/shots/dashboard.png`
- 缺失：spec §4.1 的管理员审核页

**要到 10 差什么**
1. 补齐管理员审核页（spec §4.1）
2. 删除确认的二次确认缺失（spec §3.4.2）

---

（其余维度同样模板）

## 亮点
- ...

## 最该优先修的 3 件事
1. ...
````

---

## 10. JSON 摘要 Schema（`grading-shared/score-schema.json`）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["team", "side", "total", "grade", "dimensions", "graded_at"],
  "properties": {
    "team": { "type": "string" },
    "side": { "enum": ["frontend", "backend"] },
    "total": { "type": "number", "minimum": 0, "maximum": 100 },
    "grade": { "enum": ["S", "A", "B", "C", "D"] },
    "dimensions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "score", "weight", "weighted"],
        "properties": {
          "name": { "type": "string" },
          "score": { "type": ["number", "null"] },
          "weight": { "type": "number" },
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
    "evidence_count": { "type": "integer" },
    "spec_sha": { "type": "string" },
    "project_sha": { "type": "string" },
    "graded_at": { "type": "string", "format": "date-time" }
  }
}
```

12 份 JSON 可用 `jq` 一行汇总成班级 leaderboard。

---

## 11. 证据硬约束（`grading-shared/evidence-requirements.md`）

- 任何打分 ≥ 7 或 ≤ 4 的维度 **必须至少 2 条证据**（file:line / 截图 / curl log）
- 5–6 分维度至少 1 条证据
- 证据缺失的打分视为无效，skill 强制 Claude 补齐
- 所有证据汇总进 `.grading/` 目录，报告中相对路径引用

---

## 12. Anti-patterns 示例（给这类文件感受密度）

### 前端 AI slop 特征（节选）

- 全部 `gray-100/200/…` 的灰灰白白调色板
- 默认 shadcn 未改主题色
- 所有卡片同 `rounded-lg shadow`
- 按钮都是 `bg-blue-500 hover:bg-blue-600`
- 无 `focus-visible` 环
- 空状态只有一句 "No data"
- 错误态等于 `alert(err)`
- 没有 skeleton/loading，接口一慢就白屏

### 后端反模式（节选）

- 控制器里写业务逻辑（未分层）
- 裸 `try/except: pass` 吞异常
- N+1 查询（循环里 query）
- 错误响应结构每个接口都不同
- 写操作不幂等，重试就重复创建
- 日志只有 `print` 或 `console.log`
- 迁移直接改 schema，无 migration 脚本

---

## 13. 成功标准

- 同一个项目被同一个模型评分两次，总分差距 ≤ 5
- 报告中每个维度分数都有证据支撑（evidence-requirements 的硬约束）
- 12 份 JSON 能用 `jq` 一行脚本汇总
- 学员拿到报告后，能清楚知道"下一步改什么"而不是只看到分数
- `references/` 里的内容足够深入，Claude 在不熟的技术栈上也能稳定评分

---

## 14. 开放问题（实施阶段再定）

- `calibration/benchmark-projects.md` 的样例来自哪里？建议：拿前几次培训的真实项目脱敏
- `probes/` 里的脚本是否跨语言/栈通用？建议：按主流栈分子文件
- 汇总脚本是 bash + jq 还是写个小 Node/Python 工具？—— 倾向 bash + jq，零依赖
