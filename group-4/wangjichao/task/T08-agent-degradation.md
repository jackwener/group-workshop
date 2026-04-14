# T08 — Agent 三级降级编排

| 项 | 值 |
|---|---|
| 任务ID | T08 |
| 所属 WBS | W3 Agent 编排 |
| 里程碑 | **S2** 问答核心 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T01（项目脚手架）, T09（CoPaw Provider）, T10（百炼 Provider） |
| 并行关系 | 与 T02, T03, T04 并行；完成后解锁 T06 |
| 产出文件 | `backend/agent.py` |

## 1. 任务目标

实现 `agent.py` 中的三级降级编排逻辑：CoPaw → 百炼 → Demo，按顺序尝试，静默降级，返回统一结果。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `08` 架构 | §4 | 三级降级链路：CoPaw → 百炼 → Demo |
| `08` 架构 | §2 | Agent 层：降级编排 + 结果组装，禁止感知 HTTP |
| `07` 非功能 | §1.2 | 不可跳级、静默执行、Demo 始终可用 |
| `08` 架构 | §4 | CoPaw 超时 20s，百炼超时 120s |

## 3. 核心接口

```python
class CoPawAgent:
    def ask(self, query: str, session_id: str) -> dict:
        """
        三级降级编排：
        1. CoPaw (if IRA_COPAW_*_URL configured) → {answer, source:"copaw", llm:True}
        2. 百炼 (if DASHSCOPE_API_KEY configured) → {answer, source:"bailian", llm:True}
        3. Demo (always available) → {answer, source:"demo", llm:False}
        
        返回：
        {
            "answer": str,
            "answer_source": "copaw" | "bailian" | "demo",
            "llm_used": bool,
            "model": str | None
        }
        """
```

## 4. 降级规则

| 级别 | Provider | 配置检测 | 超时 | 失败行为 |
|------|----------|----------|------|----------|
| 1 | CoPaw | `IRA_COPAW_*_URL` 非空 | 20s | 返回 None，静默降级 |
| 2 | 百炼 | `DASHSCOPE_API_KEY` 非空 | 120s | 返回 None，静默降级 |
| 3 | Demo | 始终可用 | 0s | 纯字符串拼接，永不失败 |

**Demo 模式输出示例**：
```python
f"【离线演示】您询问了：{query}。这是一个演示回复，实际使用请配置 LLM 服务。"
```

## 5. 验收标准（AC）

| # | 验收条件 | 关联 TC |
|---|---------|---------|
| AC-01 | 配置 CoPaw → answer_source='copaw', llm_used=True | TC-M01-001 |
| AC-02 | CoPaw 失败 → 自动尝试百炼 | TC-M01-004 |
| AC-03 | 百炼失败 → 自动尝试 Demo | TC-M01-004 |
| AC-04 | 无任何 Key → 直接返回 Demo | TC-M01-004 |
| AC-05 | Demo 模式返回 llm_used=False, model=None |  |
| AC-06 | 降级过程无异常抛出（静默） |  |
| AC-07 | CoPaw 超时 ≤ 20s |  |
| AC-08 | 建议 TDD：先写降级分支测试再实现 |  |
