import os
import shutil
import pytest
from backend.app import create_app

TEST_DIR = os.path.join(os.path.dirname(__file__), "..", "test_data_api")


@pytest.fixture
def client():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    app = create_app(data_dir=TEST_DIR)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)


def _create_session(client, title="测试会话"):
    resp = client.post("/api/v1/agent/sessions", json={"title": title})
    return resp.get_json()


# ========== TC-M01-020: GET /sessions ==========

class TestGetSessions:
    def test_returns_200_with_sessions_array(self, client):
        resp = client.get("/api/v1/agent/sessions")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)
        assert "traceId" in data


# ========== TC-M01-021: POST /sessions ==========

class TestCreateSession:
    def test_returns_201_with_required_fields(self, client):
        resp = client.post("/api/v1/agent/sessions", json={"title": "新会话"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert "session_id" in data
        assert "title" in data
        assert "created_at" in data
        assert "query_count" in data
        assert "traceId" in data
        assert data["query_count"] == 0


# ========== TC-M01-022: POST /sessions title too long ==========

class TestCreateSessionTitleTooLong:
    def test_returns_400_invalid_session_title(self, client):
        resp = client.post("/api/v1/agent/sessions", json={"title": "x" * 101})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_SESSION_TITLE"


# ========== TC-M01-023: DELETE /sessions/<id> ==========

class TestDeleteSession:
    def test_returns_200_with_message(self, client):
        session = _create_session(client)
        resp = client.delete(f"/api/v1/agent/sessions/{session['session_id']}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["message"] == "会话已删除"
        assert "deleted_records" in data
        assert "traceId" in data


# ========== TC-M01-024: DELETE nonexistent session ==========

class TestDeleteNonexistentSession:
    def test_returns_404_session_not_found(self, client):
        resp = client.delete("/api/v1/agent/sessions/nonexistent-id")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "SESSION_NOT_FOUND"


# ========== TC-M01-025: DELETE cascade ==========

class TestDeleteSessionCascade:
    def test_cascade_deletes_records(self, client):
        session = _create_session(client)
        sid = session["session_id"]
        # Ask a question to create a record
        client.post("/api/v1/agent/ask", json={"query": "test question", "session_id": sid})
        resp = client.delete(f"/api/v1/agent/sessions/{sid}")
        data = resp.get_json()
        assert data["deleted_records"] >= 1


# ========== TC-M01-001~004: POST /ask ==========

class TestAskEndpoint:
    def test_ask_returns_answer(self, client):
        session = _create_session(client)
        resp = client.post("/api/v1/agent/ask", json={
            "query": "你好",
            "session_id": session["session_id"],
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "answer" in data
        assert "llm_used" in data
        assert "answer_source" in data
        assert "response_time_ms" in data
        assert "traceId" in data

    def test_ask_empty_query(self, client):
        session = _create_session(client)
        resp = client.post("/api/v1/agent/ask", json={
            "query": "",
            "session_id": session["session_id"],
        })
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "EMPTY_QUERY"

    def test_ask_query_too_long(self, client):
        session = _create_session(client)
        resp = client.post("/api/v1/agent/ask", json={
            "query": "x" * 501,
            "session_id": session["session_id"],
        })
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_QUERY"

    def test_ask_session_not_found(self, client):
        resp = client.post("/api/v1/agent/ask", json={
            "query": "hello",
            "session_id": "nonexistent",
        })
        assert resp.status_code == 404
        assert resp.get_json()["error"]["code"] == "SESSION_NOT_FOUND"


# ========== TC-M01-005: GET /capabilities ==========

class TestCapabilities:
    def test_returns_200_with_fields(self, client):
        resp = client.get("/api/v1/agent/capabilities")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "copaw_configured" in data
        assert "bailian_configured" in data
        assert "traceId" in data
        assert isinstance(data["copaw_configured"], bool)
        assert isinstance(data["bailian_configured"], bool)


# ========== TC-M01-006: POST /ask llm_used type ==========

class TestAskLlmUsedType:
    def test_llm_used_is_bool(self, client):
        session = _create_session(client)
        resp = client.post("/api/v1/agent/ask", json={
            "query": "hello",
            "session_id": session["session_id"],
        })
        data = resp.get_json()
        assert isinstance(data["llm_used"], bool)


# ========== TC-M01-007: POST /ask missing session_id ==========

class TestAskMissingSessionId:
    def test_returns_400_missing_session_id(self, client):
        resp = client.post("/api/v1/agent/ask", json={"query": "hello"})
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "MISSING_SESSION_ID"


# ========== TC-M01-030/031: GET /sessions/<id>/records ==========

class TestGetRecords:
    def test_returns_records_array(self, client):
        session = _create_session(client)
        sid = session["session_id"]
        client.post("/api/v1/agent/ask", json={"query": "hi", "session_id": sid})
        resp = client.get(f"/api/v1/agent/sessions/{sid}/records")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "records" in data
        assert isinstance(data["records"], list)
        assert len(data["records"]) >= 1
        rec = data["records"][0]
        expected_fields = {"record_id", "session_id", "query", "answer",
                           "llm_used", "model", "response_time_ms", "answer_source", "timestamp"}
        assert expected_fields.issubset(set(rec.keys()))

    def test_empty_records_returns_empty_list(self, client):
        session = _create_session(client)
        resp = client.get(f"/api/v1/agent/sessions/{session['session_id']}/records")
        data = resp.get_json()
        assert data["records"] == []

    def test_nonexistent_session_returns_404(self, client):
        resp = client.get("/api/v1/agent/sessions/nonexistent/records")
        assert resp.status_code == 404
        assert resp.get_json()["error"]["code"] == "SESSION_NOT_FOUND"
