# Task: 投研问答助手 - 前端 UI 开发

## 任务概述
基于 spec-team 规格文档，实现投研问答助手的 React 前端界面，包含 Header、Sidebar、Main 内容区和输入区域。

## 参考文档
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/04-产品需求说明.md` - 产品需求与业务场景
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/05-用户故事与验收标准.md` - US-001~US-008 用户故事与 AC
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/06-功能规格说明.md` - UI/UX 行为规格
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/09-API接口规格.md` - API 契约定义
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/10-数据模型与存储规格.md` - 数据模型与 State 定义

## 技术栈
- React 18 + Vite
- CSS Modules
- 后端 API: `/api/v1/agent/*`

## 项目路径
`/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/project/frontend`

## 功能范围

### 1. Header 区域 (US-008)
- 标题展示："投研问答助手"
- 能力状态芯片：根据 `GET /capabilities` 响应显示
  - CoPaw 已配置 → 绿色边框芯片
  - 百炼已配置 → 蓝色边框芯片  
  - 均未配置 → 灰色边框"离线演示"

### 2. Sidebar 会话管理 (US-001/002/003/005)
- 会话列表：按 `updated_at` 倒序排列
- 新建会话按钮：调用 `POST /sessions`
- 删除会话：确认弹窗 → 调用 `DELETE /sessions/{id}`
- 选中会话高亮：点击后加载该会话记录
- 自动命名：首次问答后标题更新为 query 前20字

### 3. Main 内容区 - 三态渲染
- **A 空状态**：`currentSession === null` 时显示引导文案
- **B 常见问题**：有会话但无记录时，显示4个预设问题卡片
  - 问题1: "分析新能源行业最新趋势"
  - 问题2: "对比宁德时代和比亚迪的财务指标"
  - 问题3: "半导体行业本周研报观点汇总"
  - 问题4: "医药板块投资建议有哪些"
- **C 对话历史**：正序渲染问答卡片

### 4. 问答记录卡片 (US-001/006)
- 用户问题气泡（右上角，浅蓝色背景）
- AI 回答文本（左侧，白色背景，支持 Markdown）
- 来源标签：根据 `answer_source` 显示
  - `copaw` → 蓝色"CoPaw"标签
  - `bailian` → 绿色"百炼"标签
  - `demo` → 灰色"离线演示"标签
- 响应时间：`{response_time_ms}ms`
- 时间戳：格式 "HH:mm"

### 5. 输入区域 (US-001/004)
- 多行文本框：3行，placeholder "请输入您的问题..."
- 快捷发送：Ctrl+Enter
- 发送按钮：loading 时 disabled，显示"发送中..."
- 导出按钮：点击弹出格式选择（JSON/TXT）→ 下载

### 6. 状态管理
```typescript
interface State {
  sessions: Session[];
  currentSession: Session | null;
  records: QARecord[];
  query: string;
  loading: boolean;
  error: string | null;
  capabilities: Capabilities | null;
  showDeleteConfirm: boolean;
  showExportModal: boolean;
}
```

### 7. 错误处理
根据后端 `error.code` 显示对应提示：
- `EMPTY_QUERY` → "请输入问题"
- `INVALID_QUERY` → "问题过长，请控制在500字符以内"
- `SESSION_NOT_FOUND` → "会话不存在或已删除"
- `INTERNAL_ERROR` → "服务异常，请稍后重试"

## API 调用清单
| 功能 | 方法 | 端点 |
|------|------|------|
| 获取能力状态 | GET | `/api/v1/agent/capabilities` |
| 获取会话列表 | GET | `/api/v1/agent/sessions` |
| 新建会话 | POST | `/api/v1/agent/sessions` |
| 删除会话 | DELETE | `/api/v1/agent/sessions/{id}` |
| 获取会话记录 | GET | `/api/v1/agent/sessions/{id}/records` |
| 提交问答 | POST | `/api/v1/agent/ask` |
| 导出记录 | POST | `/api/v1/agent/export` |

## 验收标准
- [ ] Header 能力芯片正确显示 LLM 配置状态
- [ ] Sidebar 会话列表按时间倒序排列
- [ ] 新建/删除/切换会话功能正常
- [ ] Main 区三态渲染逻辑正确
- [ ] 问答卡片展示来源标签和响应时间
- [ ] 输入框支持 Ctrl+Enter 快捷发送
- [ ] 导出功能支持 JSON/TXT 格式选择
- [ ] 错误提示与后端 error.code 对应

## 优先级
P0 - 核心功能，必须完成

## 依赖
- 后端 API 服务已启动
- 无其他前端任务依赖，可并行开发
