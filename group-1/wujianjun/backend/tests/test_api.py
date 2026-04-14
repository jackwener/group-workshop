"""
API 集成测试
对齐 13-测试策略与质量门禁 §3.3 TC-M01-021~040
"""
import pytest
from app import create_app
from app.core.storage import Storage


@pytest.fixture
def client():
    """创建测试客户端"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        app = create_app()
        app.config["TESTING"] = True
        
        # 使用临时存储
        with app.app_context():
            from app.api import routes
            routes.storage = Storage(data_dir=tmpdir)
        
        yield app.test_client()


class TestCapabilitiesAPI:
    """能力探测 API 测试 - TC-M01-039~040"""
    
    def test_get_capabilities(self, client):
        """TC-M01-039: GET /capabilities 能力探测"""
        response = client.get("/api/v1/agent/capabilities")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "traceId" in data
        assert "data" in data
        assert "copaw_configured" in data["data"]
        assert "bailian_configured" in data["data"]
        assert "mode" in data["data"]
    
    def test_get_capabilities_trace_id(self, client):
        """TC-M01-040: GET /capabilities traceId"""
        response = client.get("/api/v1/agent/capabilities")
        data = response.get_json()
        
        assert data["traceId"].startswith("tr_")
        assert len(data["traceId"]) == 35  # tr_ + 32 hex


class TestSessionAPI:
    """会话管理 API 测试 - TC-M01-021~028"""
    
    def test_post_sessions_create(self, client):
        """TC-M01-021: POST /sessions 创建"""
        response = client.post("/api/v1/agent/sessions", json={"title": "测试会话"})
        assert response.status_code == 201
        
        data = response.get_json()
        assert "data" in data
        assert data["data"]["title"] == "测试会话"
        assert "session_id" in data["data"]
    
    def test_post_sessions_default_title(self, client):
        """TC-M01-022: POST /sessions 默认标题"""
        response = client.post("/api/v1/agent/sessions", json={})
        assert response.status_code == 201
        
        data = response.get_json()
        assert data["data"]["title"] == "新会话"
    
    def test_post_sessions_title_too_long(self, client):
        """TC-M01-023: POST /sessions 标题过长"""
        response = client.post("/api/v1/agent/sessions", json={"title": "x" * 101})
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "INVALID_QUERY"
    
    def test_get_sessions_list(self, client):
        """TC-M01-024: GET /sessions 列表"""
        # 创建两个会话
        client.post("/api/v1/agent/sessions", json={"title": "会话1"})
        client.post("/api/v1/agent/sessions", json={"title": "会话2"})
        
        response = client.get("/api/v1/agent/sessions")
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data["data"]["sessions"]) == 2
        assert data["data"]["total"] == 2
    
    def test_get_sessions_pagination(self, client):
        """TC-M01-025: GET /sessions 分页"""
        # 创建 3 个会话
        for i in range(3):
            client.post("/api/v1/agent/sessions", json={"title": f"会话{i}"})
        
        response = client.get("/api/v1/agent/sessions?limit=2")
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data["data"]["sessions"]) == 2
    
    def test_delete_session(self, client):
        """TC-M01-026: DELETE /sessions/{id} 删除"""
        # 创建会话
        resp = client.post("/api/v1/agent/sessions", json={"title": "待删除"})
        session_id = resp.get_json()["data"]["session_id"]
        
        response = client.delete(f"/api/v1/agent/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["data"]["deleted_session_id"] == session_id
    
    def test_delete_session_not_found(self, client):
        """TC-M01-027: DELETE /sessions/{id} 不存在"""
        response = client.delete("/api/v1/agent/sessions/invalid_id")
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "SESSION_NOT_FOUND"
    
    def test_delete_session_cascade(self, client):
        """TC-M01-028: DELETE /sessions/{id} 级联删除"""
        # 创建会话并添加记录
        resp = client.post("/api/v1/agent/sessions", json={"title": "测试"})
        session_id = resp.get_json()["data"]["session_id"]
        
        # 添加问答记录
        client.post("/api/v1/agent/ask", json={
            "query": "测试问题",
            "session_id": session_id
        })
        
        response = client.delete(f"/api/v1/agent/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["data"]["deleted_records_count"] == 1


class TestAskAPI:
    """问答 API 测试 - TC-M01-029~035"""
    
    def test_post_ask_normal(self, client):
        """TC-M01-029: POST /ask 正常提问"""
        # 创建会话
        resp = client.post("/api/v1/agent/sessions", json={})
        session_id = resp.get_json()["data"]["session_id"]
        
        response = client.post("/api/v1/agent/ask", json={
            "query": "测试问题",
            "session_id": session_id
        })
        assert response.status_code == 200
        
        data = response.get_json()
        assert "answer" in data["data"]
        assert "llm_used" in data["data"]
        assert "answer_source" in data["data"]
    
    def test_post_ask_empty_query(self, client):
        """TC-M01-030: POST /ask 空 query"""
        response = client.post("/api/v1/agent/ask", json={
            "query": "",
            "session_id": "sess_001"
        })
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "EMPTY_QUERY"
    
    def test_post_ask_query_too_long(self, client):
        """TC-M01-031: POST /ask query 超长"""
        response = client.post("/api/v1/agent/ask", json={
            "query": "x" * 501,
            "session_id": "sess_001"
        })
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "INVALID_QUERY"
    
    def test_post_ask_invalid_session(self, client):
        """TC-M01-032: POST /ask 无效 session_id"""
        response = client.post("/api/v1/agent/ask", json={
            "query": "测试",
            "session_id": "invalid_session"
        })
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "SESSION_NOT_FOUND"
    
    def test_post_ask_returns_record_id(self, client):
        """TC-M01-033: POST /ask 返回 record_id"""
        resp = client.post("/api/v1/agent/sessions", json={})
        session_id = resp.get_json()["data"]["session_id"]
        
        response = client.post("/api/v1/agent/ask", json={
            "query": "测试",
            "session_id": session_id
        })
        data = response.get_json()
        assert "record_id" in data["data"]
        assert data["data"]["record_id"].startswith("rec_")
    
    def test_post_ask_response_time(self, client):
        """TC-M01-034: POST /ask 响应时间"""
        resp = client.post("/api/v1/agent/sessions", json={})
        session_id = resp.get_json()["data"]["session_id"]
        
        response = client.post("/api/v1/agent/ask", json={
            "query": "测试",
            "session_id": session_id
        })
        data = response.get_json()
        assert "response_time_ms" in data["data"]
        assert data["data"]["response_time_ms"] >= 0
    
    def test_post_ask_trace_id(self, client):
        """TC-M01-035: POST /ask traceId"""
        resp = client.post("/api/v1/agent/sessions", json={})
        session_id = resp.get_json()["data"]["session_id"]
        
        response = client.post("/api/v1/agent/ask", json={
            "query": "测试",
            "session_id": session_id
        })
        data = response.get_json()
        assert "traceId" in data
        assert data["traceId"].startswith("tr_")


class TestRecordsAPI:
    """问答历史 API 测试 - TC-M01-036~038"""
    
    def test_get_records(self, client):
        """TC-M01-036: GET /sessions/{id}/records 查询"""
        # 创建会话并添加记录
        resp = client.post("/api/v1/agent/sessions", json={})
        session_id = resp.get_json()["data"]["session_id"]
        
        client.post("/api/v1/agent/ask", json={
            "query": "问题1",
            "session_id": session_id
        })
        
        response = client.get(f"/api/v1/agent/sessions/{session_id}/records")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["data"]["session_id"] == session_id
        assert len(data["data"]["records"]) == 1
    
    def test_get_records_empty(self, client):
        """TC-M01-037: GET /sessions/{id}/records 空"""
        resp = client.post("/api/v1/agent/sessions", json={})
        session_id = resp.get_json()["data"]["session_id"]
        
        response = client.get(f"/api/v1/agent/sessions/{session_id}/records")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["data"]["records"] == []
        assert data["data"]["total"] == 0
    
    def test_get_records_invalid_session(self, client):
        """TC-M01-038: GET /sessions/{id}/records 无效ID"""
        response = client.get("/api/v1/agent/sessions/invalid/records")
        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "SESSION_NOT_FOUND"
