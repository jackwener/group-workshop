import pytest
import uuid
from app.services.storage import Storage

class TestStorage:
    """Storage层单元测试"""
    
    def test_create_session(self, storage):
        """TC-M01-051: 创建会话"""
        session_id = str(uuid.uuid4())
        session = storage.create_session(session_id, "测试会话")
        
        assert session['session_id'] == session_id
        assert session['title'] == "测试会话"
        assert session['query_count'] == 0
        assert 'created_at' in session
        assert 'updated_at' in session
    
    def test_create_session_default_title(self, storage):
        """TC-M01-051: 创建会话默认标题"""
        session_id = str(uuid.uuid4())
        session = storage.create_session(session_id)
        
        assert session['title'] == "新会话"
    
    def test_create_session_duplicate_id(self, storage):
        """TC-M01-051: 重复session_id报错"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "会话1")
        
        with pytest.raises(ValueError, match="already exists"):
            storage.create_session(session_id, "会话2")
    
    def test_get_sessions(self, storage):
        """TC-M01-053: 分页查询会话列表"""
        # 创建多个会话
        for i in range(5):
            storage.create_session(str(uuid.uuid4()), f"会话{i}")
        
        sessions = storage.get_sessions(page=1, page_size=3)
        assert len(sessions) == 3
        
        sessions = storage.get_sessions(page=2, page_size=3)
        assert len(sessions) == 2
    
    def test_get_sessions_order_by_updated_at(self, storage):
        """TC-M01-053: 按updated_at倒序排序"""
        session1 = storage.create_session(str(uuid.uuid4()), "会话1")
        session2 = storage.create_session(str(uuid.uuid4()), "会话2")
        
        sessions = storage.get_sessions()
        # 后创建的应该在前面
        assert sessions[0]['session_id'] == session2['session_id']
        assert sessions[1]['session_id'] == session1['session_id']
    
    def test_get_session_by_id(self, storage):
        """TC-M01-054: 根据ID获取单个会话"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "测试会话")
        
        session = storage.get_session_by_id(session_id)
        assert session is not None
        assert session['session_id'] == session_id
        assert session['title'] == "测试会话"
    
    def test_get_session_by_id_not_found(self, storage):
        """TC-M01-054: 会话不存在返回None"""
        session = storage.get_session_by_id("non-existent-id")
        assert session is None
    
    def test_update_session(self, storage):
        """TC-M01-055: 更新会话标题"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "旧标题")
        
        updated = storage.update_session(session_id, "新标题")
        assert updated['title'] == "新标题"
        assert updated['updated_at'] != updated['created_at']
    
    def test_update_session_not_found(self, storage):
        """TC-M01-055: 更新不存在的会话报错"""
        with pytest.raises(ValueError, match="not found"):
            storage.update_session("non-existent-id", "新标题")
    
    def test_delete_session(self, storage):
        """TC-M01-056: 删除会话"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "测试会话")
        
        deleted = storage.delete_session(session_id)
        assert deleted is True
        
        session = storage.get_session_by_id(session_id)
        assert session is None
    
    def test_delete_session_not_found(self, storage):
        """TC-M01-056: 删除不存在的会话返回False"""
        deleted = storage.delete_session("non-existent-id")
        assert deleted is False
    
    def test_delete_session_cascade_records(self, storage):
        """TC-M01-056: 级联删除问答记录"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "测试会话")
        
        # 添加问答记录
        storage.add_record(
            session_id=session_id,
            query="问题1",
            answer="回答1",
            llm_used=True,
            model="gpt-4",
            response_time_ms=1000,
            answer_source="copaw"
        )
        
        # 删除会话
        storage.delete_session(session_id)
        
        # 验证记录也被删除
        records = storage.get_records_by_session(session_id)
        assert len(records) == 0
    
    def test_add_record(self, storage):
        """TC-M01-057: 写入问答记录"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "测试会话")
        
        record = storage.add_record(
            session_id=session_id,
            query="测试问题",
            answer="测试回答",
            llm_used=True,
            model="gpt-4",
            response_time_ms=1500,
            answer_source="copaw"
        )
        
        assert record['query'] == "测试问题"
        assert record['answer'] == "测试回答"
        assert record['llm_used'] is True
        assert record['model'] == "gpt-4"
        assert record['response_time_ms'] == 1500
        assert record['answer_source'] == "copaw"
        assert 'record_id' in record
        assert 'timestamp' in record
    
    def test_add_record_updates_session(self, storage):
        """TC-M01-057: 添加记录更新会话query_count和updated_at"""
        session_id = str(uuid.uuid4())
        session = storage.create_session(session_id, "测试会话")
        original_updated_at = session['updated_at']
        
        storage.add_record(
            session_id=session_id,
            query="问题",
            answer="回答",
            llm_used=False,
            model=None,
            response_time_ms=100,
            answer_source="demo"
        )
        
        updated_session = storage.get_session_by_id(session_id)
        assert updated_session['query_count'] == 1
        assert updated_session['updated_at'] != original_updated_at
    
    def test_add_record_auto_rename(self, storage):
        """首次问答自动命名"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "新会话")
        
        long_query = "这是一个很长的问题，超过20个字符"
        storage.add_record(
            session_id=session_id,
            query=long_query,
            answer="回答",
            llm_used=False,
            model=None,
            response_time_ms=100,
            answer_source="demo"
        )
        
        session = storage.get_session_by_id(session_id)
        assert session['title'] == long_query[:20] + "..."
    
    def test_add_record_session_not_found(self, storage):
        """TC-M01-057: 会话不存在时报错"""
        with pytest.raises(ValueError, match="not found"):
            storage.add_record(
                session_id="non-existent-id",
                query="问题",
                answer="回答",
                llm_used=False,
                model=None,
                response_time_ms=100,
                answer_source="demo"
            )
    
    def test_get_records_by_session(self, storage):
        """TC-M01-058: 按session_id分页查询问答记录"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "测试会话")
        
        # 添加多条记录
        for i in range(5):
            storage.add_record(
                session_id=session_id,
                query=f"问题{i}",
                answer=f"回答{i}",
                llm_used=False,
                model=None,
                response_time_ms=100,
                answer_source="demo"
            )
        
        records = storage.get_records_by_session(session_id, page=1, page_size=3)
        assert len(records) == 3
    
    def test_get_records_by_session_order(self, storage):
        """TC-M01-058: 按timestamp倒序排序"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "测试会话")
        
        storage.add_record(
            session_id=session_id,
            query="问题1",
            answer="回答1",
            llm_used=False,
            model=None,
            response_time_ms=100,
            answer_source="demo"
        )
        
        storage.add_record(
            session_id=session_id,
            query="问题2",
            answer="回答2",
            llm_used=False,
            model=None,
            response_time_ms=100,
            answer_source="demo"
        )
        
        records = storage.get_records_by_session(session_id)
        assert records[0]['query'] == "问题2"
        assert records[1]['query'] == "问题1"
    
    def test_delete_records_by_session(self, storage):
        """TC-M01-059: 删除指定会话下的所有问答记录"""
        session_id = str(uuid.uuid4())
        storage.create_session(session_id, "测试会话")
        
        storage.add_record(
            session_id=session_id,
            query="问题",
            answer="回答",
            llm_used=False,
            model=None,
            response_time_ms=100,
            answer_source="demo"
        )
        
        deleted_count = storage.delete_records_by_session(session_id)
        assert deleted_count == 1
        
        records = storage.get_records_by_session(session_id)
        assert len(records) == 0
