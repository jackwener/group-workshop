import sys
import os
import time
import pytest

# 确保可以导入 backend 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage import Storage


@pytest.fixture
def store(tmp_path):
    """创建临时目录的 Storage 实例，测试间隔离"""
    return Storage(data_dir=str(tmp_path))


# ── TC-M01-040: 初始化 ──────────────────────────────────

def test_storage_init(tmp_path):
    """Storage 实例化时自动创建 JSON 文件，内容为 []"""
    store = Storage(data_dir=str(tmp_path))
    assert os.path.exists(os.path.join(str(tmp_path), 'sessions.json'))
    assert os.path.exists(os.path.join(str(tmp_path), 'qa_records.json'))
    assert os.path.exists(os.path.join(str(tmp_path), 'reports.json'))
    # 读取验证内容为空列表
    import json
    with open(os.path.join(str(tmp_path), 'sessions.json'), 'r') as f:
        assert json.load(f) == []


# ── TC-M01-041: 创建会话 ──────────────────────────────────

def test_create_session(store):
    """create_session 返回含 session_id/title/created_at/query_count=0 的 dict"""
    session = store.create_session("test-uuid-1", "测试会话")
    assert session["session_id"] == "test-uuid-1"
    assert session["title"] == "测试会话"
    assert "created_at" in session
    assert session["query_count"] == 0


# ── TC-M01-042: 获取会话列表 ──────────────────────────────

def test_get_sessions(store):
    """get_sessions 按 created_at 倒序返回多个会话"""
    store.create_session("s1", "会话1")
    time.sleep(1.1)  # 确保时间戳不同（ISO 秒级精度）
    store.create_session("s2", "会话2")

    sessions = store.get_sessions()
    assert len(sessions) == 2
    assert sessions[0]["session_id"] == "s2"  # 最新的在前
    assert sessions[1]["session_id"] == "s1"


# ── TC-M01-043: 删除会话级联 ──────────────────────────────

def test_delete_session_cascade(store):
    """delete_session 删除会话 + 级联删除 qa_records"""
    store.create_session("s1", "会话1")
    store.add_record("s1", "问题", "答案", True, "model", 100, "demo")

    # 确认记录存在
    assert len(store.get_records_by_session("s1")) == 1

    # 删除会话
    store.delete_session("s1")

    # 验证级联删除
    assert len(store.get_sessions()) == 0
    assert len(store.get_records_by_session("s1")) == 0


# ── TC-M01-044: 添加问答记录 ──────────────────────────────

def test_add_record(store):
    """add_record 写入记录 + query_count 自动 +1 + 首次自动命名"""
    store.create_session("s1", "新会话")

    record = store.add_record("s1", "这是一个测试问题用来验证自动命名", "答案", True, "qwen-plus", 100, "bailian")

    assert record["session_id"] == "s1"
    assert record["query"] == "这是一个测试问题用来验证自动命名"
    assert record["answer"] == "答案"

    # query_count 应该 +1
    sessions = store.get_sessions()
    assert sessions[0]["query_count"] == 1
    # 首次问答自动命名
    assert sessions[0]["title"] == "这是一个测试问题用来验证自动命名"[:20] + "..."


# ── TC-M01-045: 获取会话记录 ──────────────────────────────

def test_get_records_by_session(store):
    """get_records_by_session 按 session_id 过滤，无记录返回空列表"""
    store.create_session("s1", "会话1")
    store.create_session("s2", "会话2")
    store.add_record("s1", "问题1", "答案1", False, None, 0, "demo")

    assert len(store.get_records_by_session("s1")) == 1
    assert len(store.get_records_by_session("s2")) == 0  # 无记录返回空


# ── TC-M01-046: 更新会话标题 ──────────────────────────────

def test_update_session(store):
    """update_session 更新 title 后 updated_at 刷新"""
    session = store.create_session("s1", "原标题")
    original_updated = session["updated_at"]

    time.sleep(1.1)
    updated = store.update_session("s1", "新标题")

    assert updated is not None
    assert updated["title"] == "新标题"
    assert updated["updated_at"] >= original_updated

    # 不存在的会话返回 None
    assert store.update_session("non-existent", "标题") is None


# ── TC-M01-047: 删除会话记录 ──────────────────────────────

def test_delete_records_by_session(store):
    """delete_records_by_session 删除全部记录，返回删除数量"""
    store.create_session("s1", "会话1")
    store.add_record("s1", "问题1", "答案1", False, None, 0, "demo")
    store.add_record("s1", "问题2", "答案2", False, None, 0, "demo")

    deleted = store.delete_records_by_session("s1")
    assert deleted == 2
    assert len(store.get_records_by_session("s1")) == 0


# ── TC-M01-048s: 创建研报 ──────────────────────────────────

def test_create_report(store):
    """create_report 返回 dict，初始 status=pending, is_marked=false"""
    report = store.create_report("r1", "测试研报", "pdf", 1024)
    assert report["report_id"] == "r1"
    assert report["title"] == "测试研报"
    assert report["status"] == "pending"
    assert report["is_marked"] == False
    assert report["mark_status"] == "none"
    assert report["parsed_result"] is None


# ── TC-M01-049s: 分页查询研报 ──────────────────────────────

def test_get_reports_pagination(store):
    """get_reports 分页查询，支持 keyword/rating 筛选"""
    # 创建多个研报
    for i in range(15):
        store.create_report(f"r{i}", f"研报标题{i}", "pdf", 1024)

    # 分页
    result = store.get_reports(page=1, size=10)
    assert len(result["items"]) == 10
    assert result["total"] == 15
    assert result["page"] == 1

    result2 = store.get_reports(page=2, size=10)
    assert len(result2["items"]) == 5

    # keyword 筛选
    result3 = store.get_reports(keyword="标题1")
    assert result3["total"] >= 1

    # rating 筛选（无解析结果时应为空）
    result4 = store.get_reports(rating="买入")
    assert result4["total"] == 0


# ── TC-M01-050s: 保存解析结果 ──────────────────────────────

def test_save_parse_result(store):
    """save_parse_result 保存后 get_parse_result 读出一致"""
    store.create_report("r1", "测试研报", "pdf", 1024)

    parsed = {
        "title": "测试研报",
        "rating": "买入",
        "target_price": "50元",
        "core_views": ["观点1", "观点2"],
        "data_forecast": {"pe": "15.2"},
        "parse_time_ms": 500,
        "parsed_at": "2026-04-14T10:00:00Z"
    }

    store.save_parse_result("r1", parsed)
    result = store.get_parse_result("r1")

    assert result is not None
    assert result["rating"] == "买入"
    assert result["target_price"] == "50元"
    assert len(result["core_views"]) == 2


# ── TC-M01-051s: 研报对比 ──────────────────────────────────

def test_compare_reports(store):
    """compare_reports 生成含 headers + rows 的对比数据"""
    store.create_report("r1", "研报A", "pdf", 1024)
    store.create_report("r2", "研报B", "pdf", 1024)

    store.save_parse_result("r1", {
        "title": "研报A", "rating": "买入", "target_price": "50元",
        "core_views": ["观点1"], "data_forecast": {}
    })
    store.save_parse_result("r2", {
        "title": "研报B", "rating": "增持", "target_price": "30元",
        "core_views": ["观点2"], "data_forecast": {}
    })

    result = store.compare_reports(["r1", "r2"])
    assert "headers" in result
    assert "rows" in result
    assert len(result["rows"]) == 2
    assert result["rows"][0]["report_id"] in ["r1", "r2"]
