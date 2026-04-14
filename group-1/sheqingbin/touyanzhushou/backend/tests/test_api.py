"""
API 层集成测试
"""
import json


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_get_capabilities(client):
    """测试获取能力状态"""
    response = client.get("/api/v1/agent/capabilities")
    assert response.status_code == 200
    data = response.get_json()
    
    assert "traceId" in data
    assert "copaw_configured" in data
    assert "bailian_configured" in data
    assert "demo_available" in data
    assert "features" in data


# ==================== 会话管理测试 ====================

def test_create_session(client):
    """测试创建会话"""
    response = client.post(
        "/api/v1/agent/sessions",
        json={"title": "测试会话"}
    )
    assert response.status_code == 201
    data = response.get_json()
    
    assert "session_id" in data
    assert data["title"] == "测试会话"
    assert "created_at" in data
    assert data["query_count"] == 0


def test_create_session_default_title(client):
    """测试创建会话默认标题"""
    response = client.post("/api/v1/agent/sessions", json={})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "新会话"


def test_get_sessions(client):
    """测试获取会话列表"""
    # 先创建会话
    client.post("/api/v1/agent/sessions", json={"title": "会话1"})
    client.post("/api/v1/agent/sessions", json={"title": "会话2"})
    
    response = client.get("/api/v1/agent/sessions")
    assert response.status_code == 200
    data = response.get_json()
    
    assert "sessions" in data
    assert len(data["sessions"]) == 2


def test_delete_session(client):
    """测试删除会话"""
    # 创建会话
    create_response = client.post("/api/v1/agent/sessions", json={"title": "待删除"})
    session_id = create_response.get_json()["session_id"]
    
    # 删除
    response = client.delete(f"/api/v1/agent/sessions/{session_id}")
    assert response.status_code == 200
    data = response.get_json()
    
    assert data["success"] is True
    
    # 确认已删除
    get_response = client.get("/api/v1/agent/sessions")
    sessions = get_response.get_json()["sessions"]
    assert len(sessions) == 0


def test_delete_session_not_found(client):
    """测试删除不存在的会话"""
    response = client.delete("/api/v1/agent/sessions/non-existent-id")
    assert response.status_code == 404
    data = response.get_json()
    
    assert data["error"]["code"] == "SESSION_NOT_FOUND"


# ==================== 问答测试 ====================

def test_ask_success(client):
    """测试问答提交"""
    # 创建会话
    create_response = client.post("/api/v1/agent/sessions", json={})
    session_id = create_response.get_json()["session_id"]
    
    # 提交问题
    response = client.post(
        "/api/v1/agent/ask",
        json={
            "query": "测试问题",
            "session_id": session_id
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    
    assert "answer" in data
    assert "llm_used" in data
    assert "answer_source" in data
    assert "response_time_ms" in data
    assert "traceId" in data


def test_ask_empty_query(client):
    """测试空问题"""
    response = client.post(
        "/api/v1/agent/ask",
        json={"query": "", "session_id": "test-id"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "EMPTY_QUERY"


def test_ask_query_too_long(client):
    """测试问题过长"""
    response = client.post(
        "/api/v1/agent/ask",
        json={
            "query": "a" * 501,
            "session_id": "test-id"
        }
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "INVALID_QUERY"


def test_ask_missing_session_id(client):
    """测试缺少会话ID"""
    response = client.post(
        "/api/v1/agent/ask",
        json={"query": "测试问题"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]["code"] == "INVALID_QUERY"


def test_ask_session_not_found(client):
    """测试会话不存在"""
    response = client.post(
        "/api/v1/agent/ask",
        json={
            "query": "测试问题",
            "session_id": "non-existent-id"
        }
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"]["code"] == "SESSION_NOT_FOUND"


# ==================== 记录查询测试 ====================

def test_get_session_records(client):
    """测试获取会话记录"""
    # 创建会话
    create_response = client.post("/api/v1/agent/sessions", json={})
    session_id = create_response.get_json()["session_id"]
    
    # 添加记录
    client.post(
        "/api/v1/agent/ask",
        json={"query": "问题1", "session_id": session_id}
    )
    client.post(
        "/api/v1/agent/ask",
        json={"query": "问题2", "session_id": session_id}
    )
    
    # 获取记录
    response = client.get(f"/api/v1/agent/sessions/{session_id}/records")
    assert response.status_code == 200
    data = response.get_json()
    
    assert "records" in data
    assert len(data["records"]) == 2


def test_get_session_records_not_found(client):
    """测试获取不存在会话的记录"""
    response = client.get("/api/v1/agent/sessions/non-existent-id/records")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"]["code"] == "SESSION_NOT_FOUND"


# ==================== 错误处理测试 ====================

def test_invalid_json(client):
    """测试无效 JSON"""
    response = client.post(
        "/api/v1/agent/sessions",
        data="invalid json",
        content_type="application/json"
    )
    # Flask 会自动处理无效 JSON，返回 400
    assert response.status_code == 400
