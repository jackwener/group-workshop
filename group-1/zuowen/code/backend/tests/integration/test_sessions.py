"""
会话 API 集成测试 — 对齐 Spec 13 §3.1
覆盖 TC-M01-020 ~ TC-M01-025
"""
import json


class TestGetSessions:
    """TC-M01-020"""

    def test_get_sessions_empty(self, client):
        resp = client.get("/api/v1/agent/sessions")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    def test_get_sessions_with_data(self, client):
        client.post("/api/v1/agent/sessions",
                     json={"title": "会话1"})
        resp = client.get("/api/v1/agent/sessions")
        data = resp.get_json()
        assert len(data["sessions"]) == 1


class TestCreateSession:
    """TC-M01-021"""

    def test_create_session_default_title(self, client):
        resp = client.post("/api/v1/agent/sessions", json={})
        assert resp.status_code == 201
        data = resp.get_json()
        assert "traceId" in data
        assert "session_id" in data
        assert data["title"] == "新会话"
        assert data["query_count"] == 0

    def test_create_session_custom_title(self, client):
        resp = client.post("/api/v1/agent/sessions",
                           json={"title": "茅台分析"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "茅台分析"


class TestDeleteSession:
    """TC-M01-024, TC-M01-025"""

    def test_delete_session_success(self, client):
        """TC-M01-024: 正常删除"""
        create_resp = client.post("/api/v1/agent/sessions", json={})
        sid = create_resp.get_json()["session_id"]

        resp = client.delete(f"/api/v1/agent/sessions/{sid}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert data["message"] == "会话已删除"
        assert "deleted_records" in data

    def test_delete_session_not_found(self, client):
        """TC-M01-025: 不存在"""
        resp = client.delete("/api/v1/agent/sessions/nonexistent-id")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "SESSION_NOT_FOUND"
