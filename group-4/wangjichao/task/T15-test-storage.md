# T15 — Storage 层单元测试

| 项 | 值 |
|---|---|
| 任务ID | T15 |
| 所属 WBS | W6 测试门禁 |
| 里程碑 | **S1～S3** 伴随开发 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T02（Storage 会话）, T03（Storage 研报） |
| 并行关系 | 与 T16 并行 |
| 产出文件 | `backend/tests/test_storage.py` |

## 1. 任务目标

实现 Storage 层全部 16 个方法的单元测试，覆盖正常路径和边界条件。使用 pytest + 临时目录 fixture。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `13` 测试 | §3.4 | Storage 层单元测试：12 条 TC（TC-M01-040～051s） |
| `13` 测试 | §一 | L1 Unit 层：pytest，不依赖网络 |
| `13` 测试 | §四 | 质量门禁 G-UNIT：全绿阻塞合并 |
| `13` 测试 | §五 | TDD 适用场景：CRUD 写完补测试 |

## 3. 测试用例清单（对齐 `13` §3.4）

### 3.1 初始化 & 会话管理

| TC-ID | 测试函数 | 断言要点 |
|-------|----------|----------|
| TC-M01-040 | `test_storage_init` | 目录不存在时自动创建，JSON 初始化为 `[]` |
| TC-M01-041 | `test_create_session` | 返回 dict 含 session_id/title/created_at/query_count=0 |
| TC-M01-042 | `test_get_sessions` | 多个会话按 created_at 倒序 |
| TC-M01-043 | `test_delete_session_cascade` | 删除会话 + 级联删除 qa_records |
| TC-M01-046 | `test_update_session` | title 更新，updated_at 刷新 |

### 3.2 问答记录

| TC-ID | 测试函数 | 断言要点 |
|-------|----------|----------|
| TC-M01-044 | `test_add_record` | 写入记录 + query_count 自动 +1 |
| TC-M01-045 | `test_get_records_by_session` | 按 session_id 过滤，无记录返回空列表 |
| TC-M01-047 | `test_delete_records_by_session` | 删除全部记录，返回删除数量 |

### 3.3 研报管理

| TC-ID | 测试函数 | 断言要点 |
|-------|----------|----------|
| TC-M01-048s | `test_create_report` | 初始 status=pending, is_marked=false |
| TC-M01-049s | `test_get_reports_pagination` | 分页查询，支持 keyword/rating 筛选 |
| TC-M01-050s | `test_save_parse_result` | 保存解析结果含 rating/target_price/core_views |
| TC-M01-051s | `test_compare_reports` | 生成含 headers + rows 的对比数据 |

## 4. pytest fixture 设计

```python
@pytest.fixture
def tmp_storage(tmp_path):
    """创建临时目录的 Storage 实例，测试间隔离"""
    return Storage(data_dir=str(tmp_path))
```

## 5. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | `pytest tests/test_storage.py -q` 全部通过 |
| AC-02 | 覆盖全部 16 个 Storage 方法 |
| AC-03 | 每条 TC 只验证一个点，失败信息清晰 |
| AC-04 | 使用 tmp_path fixture，不污染真实数据 |
| AC-05 | 门禁 G-UNIT 达标 |
