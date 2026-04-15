"""S1 integration tests: TC-M01-020 ~ TC-M01-025"""
import uuid


class TestGetSessions:
    def test_get_sessions_empty(self, client):
        resp = client.get("/api/v1/agent/sessions")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert data["sessions"] == []

    def test_get_sessions_sorted_by_updated_at(self, client):
        # Create two sessions
        client.post("/api/v1/agent/sessions", json={"title": "First"})
        client.post("/api/v1/agent/sessions", json={"title": "Second"})

        resp = client.get("/api/v1/agent/sessions")
        data = resp.get_json()
        sessions = data["sessions"]
        assert len(sessions) == 2
        # Most recently created should be first
        assert sessions[0]["title"] == "Second"
        assert sessions[1]["title"] == "First"


class TestCreateSession:
    def test_create_session_default_title(self, client):
        resp = client.post("/api/v1/agent/sessions", json={})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "新会话"
        assert "session_id" in data
        assert "traceId" in data
        assert data["query_count"] == 0

    def test_create_session_custom_title(self, client):
        resp = client.post("/api/v1/agent/sessions", json={"title": "测试会话"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "测试会话"

    def test_create_session_title_too_long(self, client):
        resp = client.post("/api/v1/agent/sessions",
                           json={"title": "x" * 101})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_TITLE"
        assert data["error"]["details"]["max_length"] == 100


class TestDeleteSession:
    def test_delete_session_success(self, client, seed_session):
        session_id = seed_session["session_id"]
        resp = client.delete(f"/api/v1/agent/sessions/{session_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["deleted_session_id"] == session_id

        # Verify it's gone
        resp2 = client.get("/api/v1/agent/sessions")
        assert len(resp2.get_json()["sessions"]) == 0

    def test_delete_session_invalid_id(self, client):
        resp = client.delete("/api/v1/agent/sessions/not-a-uuid")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_SESSION_ID"

    def test_delete_session_not_found(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.delete(f"/api/v1/agent/sessions/{fake_id}")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "SESSION_NOT_FOUND"

    def test_delete_session_cascade(self, client, seed_session):
        session_id = seed_session["session_id"]
        # Add a Q&A record via POST /ask
        client.post("/api/v1/agent/ask", json={
            "query": "test question",
            "session_id": session_id,
        })
        # Verify record exists
        resp = client.get(f"/api/v1/agent/sessions/{session_id}/records")
        assert len(resp.get_json()["records"]) == 1

        # Delete session
        client.delete(f"/api/v1/agent/sessions/{session_id}")

        # Session gone
        resp2 = client.get("/api/v1/agent/sessions")
        assert len(resp2.get_json()["sessions"]) == 0
