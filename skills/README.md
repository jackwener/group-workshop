# Grading Skills

面向本仓库前后端分组作业的自动化打分 skills 集合，供 Qoder / Cursor / Claude Code 等 agent 直接加载使用。

## Skills 一览

| Skill | 用途 |
| --- | --- |
| `grading-frontend/` | 前端交付打分（10 维度，权重合计 100，已内联评分标尺 / 报告模板 / 证据硬约束） |
| `grading-backend/` | 后端交付打分（9 维度，权重合计 100，已内联评分标尺 / 报告模板 / 证据硬约束） |
| `score-schema.json` | 前后端共享的 summary JSON schema |

共 2 个自包含 skill + 1 个共享 schema。两个 SKILL.md 内部已包含完整的评分标尺、报告模板、证据硬约束三段，无需再跨文件引用。

## 如何使用

在 agent 中给出类似如下的 prompt：

> 请加载 `skills/grading-frontend/SKILL.md`，按其中流程对 `teams/group-2/frontend/` 的交付物打分。
> SKILL.md 内部已包含 0–10 标尺、报告模板、证据硬约束三段。
> 产出符合 `skills/score-schema.json` 的 `summary.json` 以及 Markdown 报告，
> 所有文件写入 `.grading/group-2/frontend/`。

后端同理，改用 `skills/grading-backend/SKILL.md`。

## 目录树

```
skills/
├── README.md                    # 本文件
├── score-schema.json            # summary.json 的 JSON Schema（前后端共享）
├── grading-frontend/
│   ├── SKILL.md                 # 前端打分入口（10 维度，内联标尺/模板/证据）
│   ├── anti-patterns.md         # 常见扣分反模式
│   ├── probes/                  # 自动化探针脚本
│   └── examples/                # 示例
└── grading-backend/
    ├── SKILL.md                 # 后端打分入口（9 维度，内联标尺/模板/证据）
    ├── anti-patterns.md
    ├── probes/
    └── examples/
```

## 产出位置

所有打分产物写入仓库根目录下的 `.grading/<team>/<side>/`，该目录已加入 `.gitignore`，不会污染主干。典型结构：

```
.grading/
└── group-2/
    ├── frontend/
    │   ├── summary.json
    │   ├── report.md
    │   └── evidence/
    └── backend/
        └── ...
```

## 自检

仓库根目录运行：

```bash
./scripts/validate-grading.sh
```

会依次检查 schema 存在且合法、两份 SKILL.md 包含必要段落、sample 能过 ajv、前后端 SKILL.md 的维度数与权重合计、anti-patterns 非空，以及 probe 脚本可执行且语法合法。

## 相关文档

- Spec：`docs/grading-spec.md`
- Plan：`docs/grading-plan.md`
