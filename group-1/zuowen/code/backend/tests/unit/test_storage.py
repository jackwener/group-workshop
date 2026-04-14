"""
Storage 单元测试 — 对齐 Spec 13 §3.3
覆盖 TC-M01-040 ~ TC-M01-047
"""
import os
import pytest
from app.storage.storage import Storage


@pytest.fixture
def storage(tmp_path):
    """使用 pytest tmp_path 创建临时 Storage"""
    return Storage(data_dir=str(tmp_path / "data"))


class TestStorageInit:
    """TC-M01-040: Storage 初始化"""

    def test_auto_create_dir(self, tmp_path):
        data_dir = str(tmp_path / "nonexistent" / "data")
        assert not os.path.exists(data_dir)
        Storage(data_dir=data_dir)
        assert os.path.exists(data_dir)
        assert os.path.isfile(os.path.join(data_dir, "sessions.json"))
        assert os.path.isfile(os.path.join(data_dir, "qa_records.json"))


class TestSessionCRUD:
    """TC-M01-041 ~ TC-M01-043, TC-M01-046"""

    def test_create_session(self, storage):
        """TC-M01-041"""
        session = storage.create_session(title="测试会话")
        assert "session_id" in session
        assert session["title"] == "测试会话"
        assert session["query_count"] == 0
        assert "created_at" in session

    def test_get_sessions(self, storage):
        """TC-M01-042"""
        storage.create_session(title="会话1")
        storage.create_session(title="会话2")
        sessions = storage.get_sessions()
        assert len(sessions) == 2

    def test_delete_session_cascade(self, storage):
        """TC-M01-043: 删除 + 级联"""
        session = storage.create_session(title="待删除")
        sid = session["session_id"]
        storage.add_record(sid, "q1", "a1")
        storage.add_record(sid, "q2", "a2")
        deleted = storage.delete_session(sid)
        assert deleted == 2
        assert storage.get_session(sid) is None
        assert storage.get_records_by_session(sid) == []

    def test_delete_session_not_found(self, storage):
        """删除不存在的会话"""
        result = storage.delete_session("nonexistent-id")
        assert result is None

    def test_update_session(self, storage):
        """TC-M01-046"""
        session = storage.create_session(title="旧标题")
        sid = session["session_id"]
        updated = storage.update_session(sid, title="新标题", query_count=5)
        assert updated["title"] == "新标题"
        assert updated["query_count"] == 5


class TestRecordCRUD:
    """TC-M01-044 ~ TC-M01-045, TC-M01-047"""

    def test_add_record(self, storage):
        """TC-M01-044: 添加记录 + query_count +1"""
        session = storage.create_session(title="测试")
        sid = session["session_id"]
        record = storage.add_record(sid, "茅台研报", "这是回答")
        assert record["query"] == "茅台研报"
        assert record["session_id"] == sid
        # query_count 应该 +1
        updated_session = storage.get_session(sid)
        assert updated_session["query_count"] == 1

    def test_auto_rename_on_first_query(self, storage):
        """首次问答自动命名（Spec 10 §6）"""
        session = storage.create_session(title="新会话")
        sid = session["session_id"]
        long_query = "贵州茅台2026年第一季度研报深度分析与未来展望报告"
        storage.add_record(sid, long_query, "回答内容")
        updated = storage.get_session(sid)
        assert updated["title"] == long_query[:20] + "..."

    def test_short_query_no_ellipsis(self, storage):
        """短问题不加省略号"""
        session = storage.create_session(title="新会话")
        sid = session["session_id"]
        storage.add_record(sid, "茅台研报", "回答内容")
        updated = storage.get_session(sid)
        assert updated["title"] == "茅台研报"

    def test_get_records_by_session(self, storage):
        """TC-M01-045"""
        s1 = storage.create_session(title="会话1")
        s2 = storage.create_session(title="会话2")
        storage.add_record(s1["session_id"], "q1", "a1")
        storage.add_record(s2["session_id"], "q2", "a2")
        storage.add_record(s1["session_id"], "q3", "a3")
        records = storage.get_records_by_session(s1["session_id"])
        assert len(records) == 2
        assert records[0]["query"] == "q1"

    def test_delete_records_by_session(self, storage):
        """TC-M01-047"""
        session = storage.create_session(title="测试")
        sid = session["session_id"]
        storage.add_record(sid, "q1", "a1")
        storage.add_record(sid, "q2", "a2")
        deleted = storage.delete_records_by_session(sid)
        assert deleted == 2
        assert storage.get_records_by_session(sid) == []
