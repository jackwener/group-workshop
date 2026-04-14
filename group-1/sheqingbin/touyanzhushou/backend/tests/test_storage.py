"""
Storage 层单元测试
"""
import pytest


def test_create_session(storage):
    """测试创建会话"""
    session = storage.create_session("测试会话")
    
    assert session["title"] == "测试会话"
    assert "session_id" in session
    assert "created_at" in session
    assert "updated_at" in session
    assert session["query_count"] == 0


def test_create_session_default_title(storage):
    """测试创建会话默认标题"""
    session = storage.create_session()
    assert session["title"] == "新会话"


def test_create_session_title_truncation(storage):
    """测试标题截断"""
    long_title = "这是一个非常长的标题，超过23个字符"
    session = storage.create_session(long_title)
    assert len(session["title"]) <= 23


def test_get_sessions(storage):
    """测试获取会话列表"""
    # 创建两个会话
    session1 = storage.create_session("会话1")
    session2 = storage.create_session("会话2")
    
    sessions = storage.get_sessions()
    
    assert len(sessions) == 2
    # 按更新时间倒序
    assert sessions[0]["session_id"] == session2["session_id"]


def test_get_session(storage):
    """测试获取单个会话"""
    session = storage.create_session("测试")
    
    found = storage.get_session(session["session_id"])
    assert found is not None
    assert found["title"] == "测试"
    
    # 不存在的会话
    not_found = storage.get_session("non-existent-id")
    assert not_found is None


def test_delete_session(storage):
    """测试删除会话"""
    session = storage.create_session("待删除")
    session_id = session["session_id"]
    
    # 删除成功
    result = storage.delete_session(session_id)
    assert result is True
    
    # 确认已删除
    assert storage.get_session(session_id) is None
    
    # 重复删除返回 False
    result = storage.delete_session(session_id)
    assert result is False


def test_delete_session_cascade(storage):
    """测试级联删除记录"""
    session = storage.create_session("测试")
    session_id = session["session_id"]
    
    # 添加记录
    storage.add_record(
        session_id=session_id,
        query="测试问题",
        answer="测试回答",
        llm_used=False,
        model=None,
        response_time_ms=100,
        answer_source="demo"
    )
    
    # 删除会话
    storage.delete_session(session_id)
    
    # 确认记录也被删除
    records = storage.get_records_by_session(session_id)
    assert len(records) == 0


def test_add_record(storage):
    """测试添加问答记录"""
    session = storage.create_session("测试")
    session_id = session["session_id"]
    
    record = storage.add_record(
        session_id=session_id,
        query="测试问题",
        answer="测试回答",
        llm_used=True,
        model="test-model",
        response_time_ms=1500,
        answer_source="copaw"
    )
    
    assert record["query"] == "测试问题"
    assert record["answer"] == "测试回答"
    assert record["llm_used"] is True
    assert record["model"] == "test-model"
    assert record["answer_source"] == "copaw"
    assert "id" in record
    assert "timestamp" in record


def test_add_record_increments_query_count(storage):
    """测试添加记录增加 query_count"""
    session = storage.create_session("测试")
    session_id = session["session_id"]
    
    # 添加第一条记录
    storage.add_record(
        session_id=session_id,
        query="问题1",
        answer="回答1",
        llm_used=False,
        model=None,
        response_time_ms=100,
        answer_source="demo"
    )
    
    session = storage.get_session(session_id)
    assert session["query_count"] == 1


def test_add_record_auto_rename(storage):
    """测试首次问答自动命名"""
    session = storage.create_session("新会话")
    session_id = session["session_id"]
    
    # 首次问答
    storage.add_record(
        session_id=session_id,
        query="这是一个很长的测试问题，用于验证自动命名功能",
        answer="回答",
        llm_used=False,
        model=None,
        response_time_ms=100,
        answer_source="demo"
    )
    
    session = storage.get_session(session_id)
    # 标题应为问题前20字 + ...
    assert session["title"] == "这是一个很长的测试问题，用于..."


def test_get_records_by_session(storage):
    """测试获取会话记录"""
    session = storage.create_session("测试")
    session_id = session["session_id"]
    
    # 添加两条记录
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
    assert len(records) == 2
    # 按时间正序
    assert records[0]["query"] == "问题1"
    assert records[1]["query"] == "问题2"


def test_delete_records_by_session(storage):
    """测试删除会话的所有记录"""
    session = storage.create_session("测试")
    session_id = session["session_id"]
    
    # 添加记录
    storage.add_record(
        session_id=session_id,
        query="问题",
        answer="回答",
        llm_used=False,
        model=None,
        response_time_ms=100,
        answer_source="demo"
    )
    
    # 删除记录
    count = storage.delete_records_by_session(session_id)
    assert count == 1
    
    # 确认已删除
    records = storage.get_records_by_session(session_id)
    assert len(records) == 0
