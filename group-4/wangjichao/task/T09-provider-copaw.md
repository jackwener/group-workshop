# T09 — Provider：CoPaw 桥接

| 项 | 值 |
|---|---|
| 任务ID | T09 |
| 所属 WBS | W3 Agent 编排 |
| 里程碑 | **S2** 问答核心 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T01（项目脚手架） |
| 并行关系 | 与 T10 并行；完成后解锁 T08 |
| 产出文件 | `backend/copaw_bridge.py` |

## 1. 任务目标

实现 CoPaw 桥接层，通过 HTTP 调用 CoPaw 外部 API，返回问答结果。配置不存在时返回 None。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `08` 架构 | §2 | Provider 层：HTTP 调用外部 API，禁止操作本地存储 |
| `08` 架构 | §4 | CoPaw：`IRA_COPAW_*_URL` 环境变量，超时 20s，失败返回 None |
| `07` 非功能 | §4.1 | LLM API Key 通过环境变量存储，禁止硬编码 |

## 3. 核心接口

```python
class CoPawBridge:
    def __init__(self):
        self.base_url = os.getenv("IRA_COPAW_BASE_URL")
        self.ask_url = os.getenv("IRA_COPAW_ASK_URL")
    
    def is_configured(self) -> bool:
        """检测 CoPaw 是否已配置"""
    
    def ask(self, query: str, session_id: str) -> dict | None:
        """
        调用 CoPaw API，返回：
        {"answer": str, "model": str} 或 None（失败时）
        超时 20s，异常静默返回 None
        """
```

## 4. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | 环境变量为空时 `is_configured()` 返回 False |
| AC-02 | 配置正确时发送 HTTP 请求到 CoPaw |
| AC-03 | 超时 20s 内未响应返回 None |
| AC-04 | 任何异常返回 None（静默降级） |
| AC-05 | 禁止操作本地文件/存储 |
