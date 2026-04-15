# Spec Document Generator - Examples

## Example 1: Filling 08-系统架构与技术选型.md

### Before (Template):
```markdown
### 1.2 架构风格

1. 前后端分离架构
2. RESTful API设计
3. 模块化组件设计
4. 【请填写】

```

### After (Filled):
```markdown
### 1.2 架构风格

1. 前后端分离架构
2. RESTful API设计
3. 模块化组件设计
4. **事件驱动架构**: 采用消息队列处理异步任务（如文件解析、LLM调用），选型 RabbitMQ，理由：解耦文件上传与解析流程，提高系统响应速度，支持任务重试和失败处理

```

---

## Example 2: Filling 10-数据模型与存储规格.md

### Before (Template):
```markdown
### 5.1 Session 存储

方法: update_session
签名: 【请填写】
行为: 【请填写】
关联TC: 【请填写】

```

### After (Filled):
```markdown
### 5.1 Session 存储

方法: update_session
签名: `update_session(session_id: str, updates: Dict[str, Any]) -> Session`
行为: 根据 session_id 查找会话记录，使用 updates 字典中的字段更新会话信息（如 title、updated_at），验证字段类型后持久化到 JSON 文件，返回更新后的 Session 对象
关联TC: TC-10-001, TC-10-002

```

---

## Example 3: Filling 06-功能规格说明.md

### Before (Template):
```markdown
### 3. 会话选择交互

触发: 【请填写】
API调用: 【请填写】
行为: 【请填写】

```

### After (Filled):
```markdown
### 3. 会话选择交互

触发: 用户在左侧会话列表点击某个会话项
API调用: `GET /api/sessions/{session_id}` 获取会话详情，`GET /api/sessions/{session_id}/records` 获取问答历史
行为: 
1. 高亮选中的会话项
2. 主内容区加载该会话的标题和问答历史记录
3. 更新URL路径为 `/session/{session_id}`
4. 启用底部输入框，允许用户继续提问

```

---

## Example 4: Filling 07-非功能需求与约束.md

### Before (Template):
```markdown
### 1.1 性能指标

- API响应时间: < 500ms
- 【请补充其他延迟指标】

约束来源: 【请填写】

```

### After (Filled):
```markdown
### 1.1 性能指标

- API响应时间: < 500ms
- 页面首次加载时间: < 2s
- 文件上传处理时间: < 3s (10MB以内PDF)
- 问答历史记录加载: < 1s (100条以内)

约束来源: 来源=04 R-01, 来源=05 US-001 AC-3

```

---

## Example 5: Filling 11-安全设计规格.md

### Before (Template):
```markdown
### 2.1 认证机制

【请填写当前认证状态】

```

### After (Filled):
```markdown
### 2.1 认证机制

当前教学版状态: 无认证，开放访问。所有API端点无需身份验证即可调用。

生产环境建议: 
1. 实施 JWT Token 认证
2. 添加用户注册/登录流程
3. 实现基于角色的访问控制(RBAC)
4. 添加API速率限制防止滥用

```

---

## Usage Pattern

When using this skill:

1. **Identify the document** to be filled (e.g., 08, 10, 06, 07, 11)
2. **Locate all 【填写】 markers** in the template
3. **Reference source documents** (02, 03, 04, 05, 09) for context
4. **Fill systematically** following the requirements in reference.md
5. **Validate consistency** across documents using the checklist
6. **Preserve structure** - only modify marked areas

## Common Patterns

### Pattern 1: Method Signature Filling
```
【请填写】→ `method_name(param1: Type, param2: Type) -> ReturnType`
```

### Pattern 2: Constraint with Source
```
约束内容 + 来源=XX R-XX
```

### Pattern 3: TC Reference
```
关联TC: TC-XX-XXX, TC-XX-XXX
```

### Pattern 4: Status Description
```
当前状态: [描述]
生产建议: [建议内容]
```
