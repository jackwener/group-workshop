# T10 — Provider：百炼 DashScope

| 项 | 值 |
|---|---|
| 任务ID | T10 |
| 所属 WBS | W3 Agent 编排 |
| 里程碑 | **S2** 问答核心 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T01（项目脚手架） |
| 并行关系 | 与 T09 并行；完成后解锁 T08 |
| 产出文件 | `backend/bailian_qa.py` |

## 1. 任务目标

实现百炼 DashScope Provider，通过 DashScope API 调用大模型，返回问答结果。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `08` 架构 | §2 | Provider 层：HTTP 调用外部 API |
| `08` 架构 | §4 | 百炼：`DASHSCOPE_API_KEY` 非空，超时 120s，区分多类错误码 |
| `07` 非功能 | §4.1 | API Key 环境变量存储 |

## 3. 核心接口

```python
class BailianQA:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
    
    def is_configured(self) -> bool:
        """检测百炼是否已配置"""
    
    def ask(self, query: str) -> dict | None:
        """
        调用百炼 DashScope API，返回：
        {"answer": str, "model": str} 或 None（失败时）
        超时 120s，异常静默返回 None
        """
```

## 4. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | 环境变量为空时 `is_configured()` 返回 False |
| AC-02 | 配置正确时调用 DashScope API |
| AC-03 | 返回结果含 model 字段 |
| AC-04 | 超时 120s 内未响应返回 None |
| AC-05 | 任何异常返回 None（静默降级） |
