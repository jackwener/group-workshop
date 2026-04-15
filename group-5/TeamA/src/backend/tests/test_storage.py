"""
Storage 层单元测试
对齐 13-测试策略与质量门禁.md TC-001 系列
"""
import pytest


class TestSessionCRUD:
    """会话管理 CRUD 测试"""
    
    def test_create_session(self, storage):
        """TC-001-01: 创建会话成功"""
        session = storage.create_session(title="测试会话")
        
        assert session["session_id"] is not None
        assert session["title"] == "测试会话"
        assert session["query_count"] == 0
        assert session["status"] == "active"
        assert "created_at" in session
        assert "updated_at" in session
    
    def test_get_sessions(self, storage, sample_session):
        """TC-001-01: 获取会话列表"""
        sessions = storage.get_sessions()
        
        assert len(sessions) >= 1
        assert any(s["session_id"] == sample_session["session_id"] for s in sessions)
    
    def test_update_session(self, storage, sample_session):
        """TC-001-02: 更新会话信息"""
        updated = storage.update_session(
            sample_session["session_id"],
            {"title": "更新后的标题"}
        )
        
        assert updated is not None
        assert updated["title"] == "更新后的标题"
    
    def test_delete_session(self, storage, sample_session):
        """TC-001-03: 删除会话（软删除）"""
        result = storage.delete_session(sample_session["session_id"])
        
        assert result is True
        
        # 验证会话已被软删除
        session = storage.get_session(sample_session["session_id"])
        assert session is None


class TestRecordOperations:
    """问答记录操作测试"""
    
    def test_add_record(self, storage, sample_session):
        """TC-002-02: 添加问答记录"""
        record = storage.add_record(
            session_id=sample_session["session_id"],
            query="测试问题",
            answer="测试回答",
            llm_used=True,
            model="qwen-max",
            response_time_ms=1500,
            answer_source="bailian"
        )
        
        assert record is not None
        assert record["query"] == "测试问题"
        assert record["answer"] == "测试回答"
        assert record["llm_used"] is True
        assert record["answer_source"] == "bailian"
        
        # 验证会话计数更新
        session = storage.get_session(sample_session["session_id"])
        assert session["query_count"] == 1
    
    def test_get_records_by_session(self, storage, sample_session):
        """TC-003-01: 获取会话记录列表"""
        # 添加两条记录
        storage.add_record(
            session_id=sample_session["session_id"],
            query="问题1",
            answer="回答1",
            llm_used=False,
            model=None,
            response_time_ms=500,
            answer_source="demo"
        )
        storage.add_record(
            session_id=sample_session["session_id"],
            query="问题2",
            answer="回答2",
            llm_used=False,
            model=None,
            response_time_ms=500,
            answer_source="demo"
        )
        
        records = storage.get_records_by_session(sample_session["session_id"])
        
        assert len(records) == 2
        # 验证按时间顺序排列（先添加的在前面）
        assert records[0]["query"] == "问题1"
        assert records[1]["query"] == "问题2"
    
    def test_cascade_delete(self, storage, sample_session):
        """TC-001-03: 级联删除问答记录"""
        # 添加记录
        storage.add_record(
            session_id=sample_session["session_id"],
            query="测试问题",
            answer="测试回答",
            llm_used=False,
            model=None,
            response_time_ms=500,
            answer_source="demo"
        )
        
        # 删除会话
        deleted_records = storage.delete_records_by_session(sample_session["session_id"])
        
        assert deleted_records == 1
        
        # 验证记录已被删除
        records = storage.get_records_by_session(sample_session["session_id"])
        assert len(records) == 0


class TestFileOperations:
    """文件操作测试"""
    
    def test_save_file(self, storage, sample_session):
        """TC-002-01: 保存文件元数据"""
        file_info = storage.save_file(
            session_id=sample_session["session_id"],
            file_name="test.pdf",
            file_size=1024,
            file_type="pdf",
            file_path="/tmp/test.pdf"
        )
        
        assert file_info is not None
        assert file_info["file_name"] == "test.pdf"
        assert file_info["parse_status"] == "pending"
        assert file_info["session_id"] == sample_session["session_id"]
    
    def test_update_parse_status(self, storage, sample_session):
        """TC-002-01: 更新解析状态"""
        file_info = storage.save_file(
            session_id=sample_session["session_id"],
            file_name="test.pdf",
            file_size=1024,
            file_type="pdf",
            file_path="/tmp/test.pdf"
        )
        
        updated = storage.update_parse_status(
            file_info["file_id"],
            "completed",
            parse_progress=100,
            parse_result={"title": "研报标题"}
        )
        
        assert updated is not None
        assert updated["parse_status"] == "completed"
        assert updated["parse_progress"] == 100
        assert updated["parse_result"]["title"] == "研报标题"
    
    def test_get_files_by_session(self, storage, sample_session):
        """获取会话文件列表"""
        storage.save_file(
            session_id=sample_session["session_id"],
            file_name="file1.pdf",
            file_size=1024,
            file_type="pdf",
            file_path="/tmp/file1.pdf"
        )
        storage.save_file(
            session_id=sample_session["session_id"],
            file_name="file2.docx",
            file_size=2048,
            file_type="docx",
            file_path="/tmp/file2.docx"
        )
        
        files = storage.get_files_by_session(sample_session["session_id"])
        
        assert len(files) == 2
