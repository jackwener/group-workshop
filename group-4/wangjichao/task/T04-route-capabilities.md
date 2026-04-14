# T04 — 路由层：公共模块 + GET /capabilities

| 项 | 值 |
|---|---|
| 任务ID | T04 |
| 所属 WBS | W1 路由实现 |
| 里程碑 | **S1** 前置 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T01（项目脚手架） |
| 并行关系 | 与 T02, T03, T12 并行 |
| 产出文件 | `backend/agent_bp.py`（蓝图注册 + 公共函数 + capabilities 端点） |

## 1. 任务目标

实现 Flask 蓝图注册、统一响应格式函数（`_ok` / `_err`）、traceId 生成逻辑，以及首个端点 `GET /capabilities`。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `09` API | §2 | 统一响应规范：成功含 traceId，错误含 error.code/message/details/traceId |
| `09` API | §3 | GET /capabilities 返回 copaw_configured, bailian_configured, bailian_model |
| `07` 非功能 | §3.1 | traceId 格式 `tr_{uuid.hex}`，优先复用 `X-Trace-Id` 请求头 |
| `07` 非功能 | §3.2 | 完整错误码清单（11个） |
| `08` 架构 | §2 | Route 层：参数校验 + HTTP 状态码 + traceId，禁止直接读写文件/调用 LLM |

## 3. 需要实现的功能

### 3.1 公共函数

```python
# traceId 生成（对齐 07 §3.1）
def _get_trace_id() -> str:
    """优先复用 X-Trace-Id 请求头，缺省时生成 tr_{uuid.hex}"""

# 统一成功响应（对齐 09 §2）
def _ok(data: dict, status=200) -> Response:
    """注入 traceId，返回 JSON"""

# 统一错误响应（对齐 09 §2）
def _err(code: str, message: str, status: int, details=None) -> Response:
    """返回 {"error": {"code", "message", "details", "traceId"}}"""
```

### 3.2 GET /capabilities（对齐 `09` §3）

| 字段 | 类型 | 说明 |
|------|------|------|
| `copaw_configured` | boolean | 检测 `IRA_COPAW_*_URL` 环境变量非空 |
| `bailian_configured` | boolean | 检测 `DASHSCOPE_API_KEY` 环境变量非空 |
| `bailian_model` | string\|null | 读取 `DASHSCOPE_MODEL` 环境变量 |

### 3.3 错误码常量（对齐 `09` §2）

需定义全部 11 个错误码常量，供其他路由任务（T05/T06/T07）复用：

```
EMPTY_QUERY, INVALID_QUERY, INVALID_SESSION_ID,
INVALID_FILE_TYPE, FILE_TOO_LARGE, INVALID_REPORT_SELECTION,
SESSION_NOT_FOUND, REPORT_NOT_FOUND,
PARSE_ERROR, UPSTREAM_ERROR, LLM_UNAVAILABLE
```

## 4. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | Flask 蓝图 `agent_bp` 注册成功，url_prefix = `/api/v1/agent` |
| AC-02 | `GET /api/v1/agent/capabilities` → 200，含 traceId + 三个配置字段 |
| AC-03 | traceId 格式为 `tr_` + 32位hex |
| AC-04 | 有 `X-Trace-Id` 请求头时复用该值 |
| AC-05 | `_err("EMPTY_QUERY", ...)` 返回正确的 JSON 错误结构 |
| AC-06 | 所有 11 个错误码常量已定义 |
