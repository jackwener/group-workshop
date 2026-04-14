# T16 — API 集成测试

| 项 | 值 |
|---|---|
| 任务ID | T16 |
| 所属 WBS | W6 测试门禁 |
| 里程碑 | **S2～S4** 伴随开发 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T04-T07（路由层全部端点） |
| 并行关系 | 与 T15 并行 |
| 产出文件 | `backend/tests/test_api.py` |

## 1. 任务目标

使用 Flask test_client 实现全部 14 个 API 端点的集成测试，覆盖正常路径和错误码路径。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `13` 测试 | §三 | 已有 TC：TC-M01-001～004（ask）|
| `13` 测试 | §3.1 | 会话管理 API：TC-M01-020～025 |
| `13` 测试 | §3.2 | 问答记录 API：TC-M01-030～032 |
| `13` 测试 | §3.3 | 研报管理 API：TC-M01-048～057 |
| `13` 测试 | §一 | L2 Integration 层：pytest + Flask test_client |
| `13` 测试 | §四 | 质量门禁 G-INT：全绿阻塞合并 |

## 3. 测试用例清单

### 3.1 问答提交（4 条）

| TC-ID | 断言要点 |
|-------|----------|
| TC-M01-001 | POST /ask → 200, 含 answer/llm_used/traceId |
| TC-M01-002 | 空 query → 400, EMPTY_QUERY |
| TC-M01-003 | query > 500 字符 → 400, INVALID_QUERY |
| TC-M01-004 | 无 API Key → answer_source='demo' |

### 3.2 会话管理（6 条）

| TC-ID | 断言要点 |
|-------|----------|
| TC-M01-020 | GET /sessions → 200, sessions 数组倒序 |
| TC-M01-021 | POST /sessions → 201, 含 session_id |
| TC-M01-022 | DELETE /sessions/<id> → 200, 级联删除 |
| TC-M01-023 | DELETE 不存在 → 404, SESSION_NOT_FOUND |
| TC-M01-024 | PUT /sessions/<id> → 200, title 更新 |
| TC-M01-025 | POST /sessions title > 100 → 400 |

### 3.3 问答记录（3 条）

| TC-ID | 断言要点 |
|-------|----------|
| TC-M01-030 | GET /records → 200, 有记录含 query/answer/answer_source |
| TC-M01-031 | GET /records → 200, 无记录返回空数组 |
| TC-M01-032 | GET /records 不存在 session → 404 |

### 3.4 研报管理（10 条）

| TC-ID | 断言要点 |
|-------|----------|
| TC-M01-048 | POST /reports 上传 PDF → 201, status=pending |
| TC-M01-049 | POST /reports 非 PDF/HTML → 400, INVALID_FILE_TYPE |
| TC-M01-050 | GET /reports → 200, 支持筛选 |
| TC-M01-051 | GET /reports/<id> → 200, 含 parsed_result |
| TC-M01-052 | DELETE /reports/<id> → 200, 级联删除 |
| TC-M01-053 | PUT /reports/<id>/mark → 200 |
| TC-M01-054 | POST /reports/<id>/parse → 200, 含解析结果 |
| TC-M01-055 | POST /reports/<id>/parse 耗时 < 5000ms |
| TC-M01-056 | POST /reports/compare 2-10 份 → 200 |
| TC-M01-057 | POST /reports/compare < 2 份 → 400 |

## 4. pytest fixture 设计

```python
@pytest.fixture
def client(tmp_path):
    """Flask test_client，使用临时数据目录"""
    app = create_app(data_dir=str(tmp_path))
    with app.test_client() as client:
        yield client

@pytest.fixture
def seeded_session(client):
    """预创建一个会话"""
    resp = client.post("/api/v1/agent/sessions", json={"title": "测试会话"})
    return resp.get_json()
```

## 5. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | `pytest tests/test_api.py -q` 全部通过 |
| AC-02 | 覆盖全部 14 个端点至少 1 条正常路径 |
| AC-03 | 覆盖全部 11 个错误码至少 1 条错误路径 |
| AC-04 | 每条 TC 断言 traceId 存在 |
| AC-05 | 门禁 G-INT 达标 |
| AC-06 | 共 23 条 TC |
