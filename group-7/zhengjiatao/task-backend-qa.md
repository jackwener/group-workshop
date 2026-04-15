# Task: 投研问答助手 - 后端问答与导出模块

## 任务概述
实现投研问答助手的问答提交与导出功能后端模块，包含 LLM 三级降级机制、问答记录保存、导出功能。

## 参考文档
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/04-产品需求说明.md` - SC-01/05 场景，R-04 降级规则
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/05-用户故事与验收标准.md` - US-001/004/006/007
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/09-API接口规格.md` - 端点 2/13/15
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/10-数据模型与存储规格.md` - QARecord 实体定义
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/11-安全设计规格.md` - 降级兜底策略

## 技术栈
- Python + Flask
- LLM 调用：CoPaw API → 百炼(DashScope) → Demo 离线兜底

## 项目路径
`/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/project/backend`

## 功能范围

### 1. LLM 三级降级机制 (US-006)

#### 降级顺序
1. **CoPaw** (优先级最高)
   - 检查环境变量 `COPAW_API_KEY`
   - 调用 CoPaw 桥接服务
   - 成功时 `answer_source=copaw`, `llm_used=true`

2. **百炼 (DashScope)**
   - 检查环境变量 `DASHSCOPE_API_KEY`
   - 调用阿里云百炼 API
   - 成功时 `answer_source=bailian`, `llm_used=true`

3. **Demo 离线兜底**
   - 无需配置
   - 返回预设演示回答
   - `answer_source=demo`, `llm_used=false`
   - 响应时间 ≤ 500ms

#### 降级逻辑
```python
async def ask_with_fallback(query, session_id):
    start_time = time.time()
    
    # 尝试 CoPaw
    if copaw_configured():
        try:
            answer = await call_copaw(query)
            return build_response(answer, "copaw", True)
        except:
            pass
    
    # 尝试百炼
    if bailian_configured():
        try:
            answer = await call_bailian(query)
            return build_response(answer, "bailian", True)
        except:
            pass
    
    # Demo 兜底
    answer = get_demo_answer(query)
    return build_response(answer, "demo", False)
```

### 2. 问答提交 API (POST /ask)

#### 请求参数
| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| query | string | 是 | 1-500字符 |
| session_id | string | 是 | UUID格式 |

#### 响应字段
| 字段 | 类型 | 说明 |
|------|------|------|
| traceId | string | 链路追踪ID |
| answer | string | AI回答文本 |
| llm_used | boolean | 是否使用真实LLM |
| model | string\|null | 模型标识 |
| response_time_ms | integer | 响应耗时(ms) |
| answer_source | string | copaw/bailian/demo |
| sources | array | 引用来源列表 |

#### 参数校验
| 条件 | error.code | HTTP |
|------|------------|------|
| query 为空 | EMPTY_QUERY | 400 |
| query > 500字符 | INVALID_QUERY | 400 |
| session_id 为空 | EMPTY_SESSION_ID | 400 |
| session_id 格式非法 | INVALID_SESSION_ID | 400 |
| 会话不存在 | SESSION_NOT_FOUND | 404 |

### 3. 问答记录保存
调用 Storage.add_record() 保存：
- record_id: `rec_{timestamp}_{random}`
- session_id, query, answer
- llm_used, model, answer_source
- response_time_ms
- timestamp (ISO-8601 UTC)

同时更新 Session：
- query_count += 1
- updated_at = 当前时间
- 若 query_count == 1，自动更新 title = query[:20]

### 4. 导出功能 (US-004)

#### POST /export - 导出问答记录
请求：
```json
{
  "session_id": "uuid",
  "format": "json" | "txt"
}
```

响应：
```json
{
  "traceId": "tr_xxx",
  "export_id": "exp_xxx",
  "status": "completed",
  "download_url": "/api/v1/agent/download/exp_xxx",
  "expires_at": "2025-04-15T10:35:00Z"
}
```

#### 导出格式

**JSON 格式：**
```json
{
  "session_id": "xxx",
  "title": "会话标题",
  "export_time": "2025-04-15T10:30:00Z",
  "records": [
    {
      "query": "...",
      "answer": "...",
      "timestamp": "...",
      "answer_source": "copaw"
    }
  ]
}
```

**TXT 格式：**
```
会话标题: xxx
导出时间: 2025-04-15 10:30:00
==================

[问题 1]
Q: ...
A: ...
来源: copaw
时间: 10:30

[问题 2]
...
```

#### 临时文件管理
- 生成临时文件存储导出内容
- 下载链接有效期：5分钟
- 过期后自动清理

### 5. Demo 回答模板
预设回答模板，支持关键词匹配：
- "宁德时代" → 返回宁德时代相关演示数据
- "新能源" → 返回新能源行业演示数据
- "对比" → 返回对比分析演示数据
- 默认 → 通用演示回答

### 6. 错误处理
| error.code | HTTP | 触发条件 |
|------------|------|----------|
| EMPTY_QUERY | 400 | query为空 |
| INVALID_QUERY | 400 | query超500字符 |
| EMPTY_SESSION_ID | 400 | session_id为空 |
| INVALID_SESSION_ID | 400 | ID格式非法 |
| SESSION_NOT_FOUND | 404 | 会话不存在 |
| INVALID_FORMAT | 400 | format不是json/txt |
| LLM_UNAVAILABLE | 500 | 所有LLM都失败 |

## 接口契约

### 统一响应格式
**成功：**
```json
{ "traceId": "tr_xxx", /* 业务字段 */ }
```

**错误：**
```json
{ "error": { "code": "EMPTY_QUERY", "message": "请输入问题", "traceId": "tr_xxx" } }
```

## 验收标准
- [ ] CoPaw/百炼/Demo 三级降级逻辑正确
- [ ] 降级过程对用户透明，始终返回有效回答
- [ ] answer_source 正确标识当前生效层级
- [ ] Demo 兜底响应时间 ≤ 500ms
- [ ] 问答记录正确落库，包含所有字段
- [ ] 首次问答后自动更新会话标题
- [ ] 导出支持 JSON/TXT 两种格式
- [ ] 下载链接5分钟后失效
- [ ] 参数校验返回正确的 error.code

## 优先级
P0 - 核心功能，必须完成

## 依赖
- Storage 类（来自 task-backend-session）
- 无其他任务依赖，可并行开发
