# T07 — 路由层：研报管理端点

| 项 | 值 |
|---|---|
| 任务ID | T07 |
| 所属 WBS | W1 路由实现 |
| 里程碑 | **S3** 研报功能 + **S4** 标记/解析 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T03（Storage 研报 CRUD）, T04（路由公共模块）, T11（解析引擎） |
| 并行关系 | 与 T05, T06 并行 |
| 产出文件 | `backend/agent_bp.py`（研报相关端点） |

## 1. 任务目标

实现 7 个研报管理相关 API 端点：上传、列表、详情、删除、标记、解析、对比。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `09` API | §10.1 | POST /reports — 研报上传 (multipart/form-data)，PDF/HTML ≤ 50MB |
| `09` API | §10.2 | GET /reports — 研报列表，支持 keyword/rating/page/size/sort 查询参数 |
| `09` API | §10.3 | GET /reports/<id> — 研报详情 + 解析结果 |
| `09` API | §10.4 | DELETE /reports/<id> — 删除研报 + 级联删除解析结果 |
| `09` API | §10.5 | PUT /reports/<id>/mark — 标记研报 (none/important/read) |
| `09` API | §10.6 | POST /reports/<id>/parse — 触发研报解析 |
| `09` API | §10.7 | POST /reports/compare — 多研报对比 (2-10 个 report_ids) |

## 3. 端点清单

| # | 端点 | 方法 | 成功码 | 关键校验 |
|---|------|------|--------|---------|
| 1 | `/reports` | POST | 201 | INVALID_FILE_TYPE, FILE_TOO_LARGE |
| 2 | `/reports` | GET | 200 | — |
| 3 | `/reports/<id>` | GET | 200 | REPORT_NOT_FOUND |
| 4 | `/reports/<id>` | DELETE | 200 | REPORT_NOT_FOUND |
| 5 | `/reports/<id>/mark` | PUT | 200 | REPORT_NOT_FOUND, INVALID_QUERY |
| 6 | `/reports/<id>/parse` | POST | 200 | REPORT_NOT_FOUND, PARSE_ERROR |
| 7 | `/reports/compare` | POST | 200 | INVALID_REPORT_SELECTION |

## 4. 关键实现细节

### 4.1 文件上传（POST /reports）
- 接收 `multipart/form-data`，字段 `file` + 可选 `title`
- 校验文件格式（PDF/HTML）和大小（≤ 50MB）
- 存储文件到 `backend/data/uploads/`
- 创建研报记录 status=pending

### 4.2 研报解析（POST /reports/<id>/parse）
- 调用 `report_parser.py` 解析引擎
- 状态流转：pending → parsing → completed/failed
- 解析结果包含：title, rating, target_price, core_views, data_forecast

### 4.3 研报对比（POST /reports/compare）
- 校验 report_ids 数量 2-10
- 调用 Storage.compare_reports 生成对比数据

## 5. 验收标准（AC）

| # | 验收条件 | 关联 TC |
|---|---------|---------|
| AC-01 | POST /reports 上传 PDF → 201, 含 report_id/status=pending | TC-M01-048 |
| AC-02 | POST /reports 非 PDF/HTML → 400, INVALID_FILE_TYPE | TC-M01-049 |
| AC-03 | GET /reports → 200, 支持 keyword/rating 筛选 | TC-M01-050 |
| AC-04 | GET /reports/<id> → 200, 含 parsed_result | TC-M01-051 |
| AC-05 | DELETE /reports/<id> → 200, 级联删除 | TC-M01-052 |
| AC-06 | PUT /reports/<id>/mark → 200, mark_status 正确 | TC-M01-053 |
| AC-07 | POST /reports/<id>/parse → 200, 含解析结果 | TC-M01-054 |
| AC-08 | POST /reports/compare 2-10份 → 200, 含对比表 | TC-M01-056 |
| AC-09 | POST /reports/compare <2份 → 400, INVALID_REPORT_SELECTION | TC-M01-057 |
