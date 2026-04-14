"""
Storage 层单元测试
对齐 13-测试策略与质量门禁 §3.1 TC-M01-001~010
"""
import os
import tempfile
import pytest
from app.core.storage import Storage


@pytest.fixture
def storage():
    """创建临时存储实例"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Storage(data_dir=tmpdir)


class TestSessionCRUD:
    """会话管理测试 - TC-M01-001~006"""
    
    def test_create_session(self, storage):
        """TC-M01-001: create_session 创建会话"""
        session = storage.create_session("sess_001", "测试会话")
        assert session["session_id"] == "sess_001"
        assert session["title"] == "测试会话"
        assert session["query_count"] == 0
        assert "created_at" in session
        assert "updated_at" in session
    
    def test_create_session_default_title(self, storage):
        """TC-M01-002: create_session 默认标题"""
        session = storage.create_session("sess_002")
        assert session["title"] == "新会话"
    
    def test_get_sessions_sorted(self, storage):
        """TC-M01-003: get_sessions 列表排序"""
        storage.create_session("sess_a", "会话A")
        storage.create_session("sess_b", "会话B")
        storage.create_session("sess_c", "会话C")
        
        sessions = storage.get_sessions()
        assert len(sessions) == 3
        # 按 created_at 倒序
        assert sessions[0]["session_id"] == "sess_c"
        assert sessions[1]["session_id"] == "sess_b"
        assert sessions[2]["session_id"] == "sess_a"
    
    def test_delete_session(self, storage):
        """TC-M01-004: delete_session 删除"""
        storage.create_session("sess_001")
        deleted = storage.delete_session("sess_001")
        assert deleted == 0  # 无关联记录
        
        session = storage.get_session("sess_001")
        assert session is None
    
    def test_delete_session_cascade(self, storage):
        """TC-M01-005: delete_session 级联删除"""
        storage.create_session("sess_001")
        storage.add_record("sess_001", "问题1", "答案1", True, "model", 1000, "demo")
        storage.add_record("sess_001", "问题2", "答案2", True, "model", 1000, "demo")
        
        deleted = storage.delete_session("sess_001")
        assert deleted == 2  # 删除 2 条记录
        
        records = storage.get_records_by_session("sess_001")
        assert len(records) == 0
    
    def test_update_session(self, storage):
        """TC-M01-006: update_session 更新"""
        storage.create_session("sess_001", "旧标题")
        updated = storage.update_session("sess_001", {"title": "新标题"})
        
        assert updated["title"] == "新标题"
        assert updated["updated_at"] != updated["created_at"]


class TestRecordCRUD:
    """问答记录管理测试 - TC-M01-007~010"""
    
    def test_add_record(self, storage):
        """TC-M01-007: add_record 添加记录"""
        storage.create_session("sess_001")
        record = storage.add_record(
            "sess_001", "测试问题", "测试答案",
            True, "qwen-turbo", 1500, "demo"
        )
        
        assert record["query"] == "测试问题"
        assert record["answer"] == "测试答案"
        assert record["llm_used"] is True
        assert record["answer_source"] == "demo"
        assert record["record_id"].startswith("rec_")
        
        # 验证 session 更新
        session = storage.get_session("sess_001")
        assert session["query_count"] == 1
    
    def test_get_records_by_session(self, storage):
        """TC-M01-008: get_records_by_session 查询"""
        storage.create_session("sess_001")
        storage.add_record("sess_001", "问题1", "答案1", True, "model", 1000, "demo")
        storage.add_record("sess_001", "问题2", "答案2", True, "model", 1000, "demo")
        storage.add_record("sess_001", "问题3", "答案3", True, "model", 1000, "demo")
        
        records = storage.get_records_by_session("sess_001")
        assert len(records) == 3
        # 按 timestamp 正序
        assert records[0]["query"] == "问题1"
        assert records[1]["query"] == "问题2"
        assert records[2]["query"] == "问题3"
    
    def test_delete_records_by_session(self, storage):
        """TC-M01-009: delete_records_by_session 删除"""
        storage.create_session("sess_001")
        storage.add_record("sess_001", "问题1", "答案1", True, "model", 1000, "demo")
        storage.add_record("sess_001", "问题2", "答案2", True, "model", 1000, "demo")
        
        deleted = storage.delete_records_by_session("sess_001")
        assert deleted == 2
        
        records = storage.get_records_by_session("sess_001")
        assert len(records) == 0
    
    def test_auto_rename_on_first_query(self, storage):
        """TC-M01-010: 首次问答自动命名"""
        storage.create_session("sess_001")  # query_count = 0
        
        # 首次提问
        storage.add_record("sess_001", "这是一个很长的测试问题用于验证自动命名", "答案", True, "model", 1000, "demo")
        
        session = storage.get_session("sess_001")
        assert session["query_count"] == 1
        assert session["title"] == "这是一个很长的测试问题用于..."
