# Task: 投研问答助手 - 后端系统能力模块

## 任务概述
实现投研问答助手的系统能力探测与健康检查后端模块，用于展示系统配置状态和运行健康度。

## 参考文档
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/04-产品需求说明.md` - SC-06 场景，R-08 能力状态规则
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/05-用户故事与验收标准.md` - US-008
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/09-API接口规格.md` - 端点 1/12
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/11-安全设计规格.md` - §4 能力探测安全设计

## 技术栈
- Python + Flask
- 环境变量读取

## 项目路径
`/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/project/backend`

## 功能范围

### 1. 能力探测 API (GET /capabilities)

#### 功能说明
获取系统当前配置的能力状态，用于 Header 区域展示 LLM 配置状态芯片。

#### 响应字段
| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| traceId | string | 是 | 链路追踪ID |
| copaw_configured | boolean | 是 | CoPaw LLM是否已配置 |
| bailian_configured | boolean | 是 | 百炼(DashScope)是否已配置 |
| demo_available | boolean | 是 | Demo离线兜底是否可用 |
| version | string | 是 | API版本号 |

#### 配置检测逻辑
```python
def check_capabilities():
    return {
        "copaw_configured": bool(os.getenv("COPAW_API_KEY")),
        "bailian_configured": bool(os.getenv("DASHSCOPE_API_KEY")),
        "demo_available": True,  # Demo 始终可用
        "version": "v1.0"
    }
```

#### 响应示例
```json
{
  "traceId": "tr_abc123def456",
  "copaw_configured": true,
  "bailian_configured": true,
  "demo_available": true,
  "version": "v1.0"
}
```

#### 芯片展示映射
| copaw_configured | bailian_configured | 前端展示 |
|------------------|-------------------|----------|
| true | any | CoPaw 芯片（绿色边框）|
| false | true | 百炼芯片（蓝色边框）|
| false | false | 离线演示芯片（灰色边框）|

### 2. 健康检查 API (GET /health)

#### 功能说明
获取系统健康状态和运行指标，用于运维监控和系统状态展示。

#### 响应字段
| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| traceId | string | 是 | 链路追踪ID |
| status | string | 是 | healthy/degraded/unhealthy |
| timestamp | string | 是 | 检查时间(ISO-8601) |
| services | object | 是 | 各服务状态 |
| services.llm | object | 是 | LLM服务状态 |
| services.llm.status | string | 是 | available/unavailable |
| services.llm.provider | string | 否 | copaw/bailian/demo |
| services.database | string | 是 | ok/error |
| metrics | object | 是 | 运行指标 |
| metrics.active_sessions | integer | 是 | 活跃会话数 |
| metrics.total_queries | integer | 是 | 总查询次数 |
| metrics.avg_response_time_ms | integer | 是 | 平均响应时间(ms) |
| metrics.total_reports | integer | 是 | 研报总数 |

#### 健康状态判定
| 条件 | status |
|------|--------|
| 所有服务正常 | healthy |
| 部分服务异常但可降级 | degraded |
| 核心服务不可用 | unhealthy |

#### 服务状态检测
```python
def check_health():
    # LLM 服务检测
    llm_status = "unavailable"
    provider = None
    
    if test_copaw_connection():
        llm_status = "available"
        provider = "copaw"
    elif test_bailian_connection():
        llm_status = "available"
        provider = "bailian"
    else:
        llm_status = "available"  # Demo 兜底
        provider = "demo"
    
    # 数据库检测
    db_status = "ok" if check_json_files() else "error"
    
    # 计算运行指标
    metrics = calculate_metrics()
    
    return {
        "status": determine_status(llm_status, db_status),
        "services": {
            "llm": {"status": llm_status, "provider": provider},
            "database": db_status
        },
        "metrics": metrics
    }
```

#### 响应示例
```json
{
  "traceId": "tr_abc123def456",
  "status": "healthy",
  "timestamp": "2025-04-15T10:30:00Z",
  "services": {
    "llm": {
      "status": "available",
      "provider": "copaw"
    },
    "database": "ok"
  },
  "metrics": {
    "active_sessions": 12,
    "total_queries": 156,
    "avg_response_time_ms": 1200,
    "total_reports": 25
  }
}
```

### 3. 运行指标统计

#### 指标计算
| 指标 | 计算方式 |
|------|----------|
| active_sessions | 最近24小时内有问答的会话数 |
| total_queries | QARecord 表总记录数 |
| avg_response_time_ms | 最近100条记录的平均响应时间 |
| total_reports | 研报文件总数（如有研报功能）|

#### 指标缓存
- 健康检查接口可能被频繁调用
- 建议对 metrics 进行短时间缓存（如30秒）
- 避免每次都全量计算

### 4. 安全设计

#### 访问控制
- GET /capabilities：公开访问，无需认证
- GET /health：公开访问，但可限制频率

#### 信息暴露控制
- 不返回敏感配置值（如 API Key）
- 仅返回配置状态（true/false）
- 错误信息不暴露内部细节

### 5. traceId 生成
所有 API 响应必须包含 traceId：
```python
import uuid

def generate_trace_id():
    return f"tr_{uuid.uuid4().hex[:16]}"
```

## 接口契约

### 统一响应格式
**成功：**
```json
{ "traceId": "tr_xxx", /* 业务字段 */ }
```

**错误：**
```json
{ "error": { "code": "INTERNAL_ERROR", "message": "...", "traceId": "tr_xxx" } }
```

## 验收标准
- [ ] GET /capabilities 返回正确的配置状态
- [ ] copaw_configured/bailian_configured 基于环境变量检测
- [ ] GET /health 返回正确的健康状态和运行指标
- [ ] status 字段正确判定：healthy/degraded/unhealthy
- [ ] metrics 数据准确：会话数、查询数、平均响应时间
- [ ] 所有响应包含 traceId
- [ ] 不暴露敏感配置信息

## 优先级
P1 - 重要功能，建议完成

## 依赖
- Storage 类（用于统计指标）
- 无其他任务依赖，可并行开发

## 备注
此模块相对独立，可在其他模块完成后实现，也可提前实现用于系统监控。
