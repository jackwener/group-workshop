# T03 — Storage 层：研报与解析结果 CRUD

| 项 | 值 |
|---|---|
| 任务ID | T03 |
| 所属 WBS | W2 存储层 |
| 里程碑 | **S3** 研报功能 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T01（项目脚手架） |
| 并行关系 | 与 T02 并行；完成后解锁 T07, T11 |
| 产出文件 | `backend/storage.py`（研报部分） |

## 1. 任务目标

实现 Storage 类中研报管理（6个方法）和研报解析与对比（3个方法）的完整 CRUD 逻辑。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `10` 数据模型 | §5 | Report 实体：report_id, title(≤200), file_type(pdf/html), file_size(≤50MB), file_path, status(pending/parsing/completed/failed), uploaded_at, is_marked, mark_status(none/important/read) |
| `10` 数据模型 | §6 | ParseResult 实体：report_id(FK), title, rating, target_price, core_views(≤5), data_forecast, parse_time_ms, parsed_at |
| `10` 数据模型 | §7.3 | 研报管理 6 个方法签名 |
| `10` 数据模型 | §7.4 | 研报解析与对比 3 个方法签名 |
| `10` 数据模型 | §8 | 级联删除研报时同步删除 ParseResult；状态流转 pending→parsing→completed/failed |

## 3. 需要实现的方法

### 3.1 研报管理（对齐 `10` §7.3）

| 方法 | 签名 | 关键行为 | 关联 TC |
|------|------|----------|---------|
| `create_report` | `(report_id, title, file_type, file_size) → dict` | 创建研报记录，初始 status=pending | TC-M01-048s |
| `get_reports` | `(keyword, rating, page, size) → dict` | 分页查询，支持 keyword/rating 筛选 | TC-M01-049s |
| `get_report_by_id` | `(report_id) → dict` | 获取研报详情 | TC-M01-050 |
| `delete_report` | `(report_id) → None` | 删除研报 + **级联删除**解析结果 | TC-M01-051 |
| `update_report_status` | `(report_id, status) → dict` | 更新解析状态（状态流转） | TC-M01-052 |
| `mark_report` | `(report_id, is_marked) → dict` | 标记研报为重点/已读 | TC-M01-053 |

### 3.2 研报解析与对比（对齐 `10` §7.4）

| 方法 | 签名 | 关键行为 | 关联 TC |
|------|------|----------|---------|
| `save_parse_result` | `(report_id, parsed_result) → dict` | 保存解析结果 | TC-M01-054 |
| `get_parse_result` | `(report_id) → dict` | 获取解析结果 | TC-M01-055 |
| `compare_reports` | `(report_ids, compare_fields) → dict` | 生成研报对比数据（headers + rows） | TC-M01-056 |

### 3.3 关键业务逻辑

- **状态流转**：`pending → parsing → completed / failed`
- **级联删除**：删除 Report 时同步删除对应 ParseResult
- **分页逻辑**：`get_reports` 支持 keyword 模糊匹配 title，rating 精确匹配

## 4. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | `create_report` 返回 dict，初始 status=pending, is_marked=false |
| AC-02 | `get_reports` 支持 keyword 模糊搜索 + rating 精确筛选 |
| AC-03 | `get_reports` 分页正确（page/size/total） |
| AC-04 | `delete_report` 级联删除 ParseResult |
| AC-05 | `update_report_status` 正确流转状态 |
| AC-06 | `mark_report` 支持 none/important/read 三种状态 |
| AC-07 | `save_parse_result` + `get_parse_result` 读写一致 |
| AC-08 | `compare_reports` 生成包含 headers + rows 的对比数据 |
