import os
import re
import shutil
import pytest
from backend.app import create_app

TEST_DIR = os.path.join(os.path.dirname(__file__), "..", "test_data_contract")

TRACE_ID_PATTERN = re.compile(r"^tr_[0-9a-f]{32}$")


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


def _create_session(client, title="合约测试"):
    return client.post("/api/v1/agent/sessions", json={"title": title}).get_json()


# ========== traceId format ==========

class TestTraceIdFormat:
    def test_post_sessions_trace_id(self, client):
        data = _create_session(client)
        assert TRACE_ID_PATTERN.match(data["traceId"])

    def test_get_sessions_trace_id(self, client):
        data = client.get("/api/v1/agent/sessions").get_json()
        assert TRACE_ID_PATTERN.match(data["traceId"])

    def test_delete_sessions_trace_id(self, client):
        session = _create_session(client)
        data = client.delete(f"/api/v1/agent/sessions/{session['session_id']}").get_json()
        assert TRACE_ID_PATTERN.match(data["traceId"])

    def test_ask_trace_id(self, client):
        session = _create_session(client)
        data = client.post("/api/v1/agent/ask", json={
            "query": "hello", "session_id": session["session_id"]
        }).get_json()
        assert TRACE_ID_PATTERN.match(data["traceId"])

    def test_records_trace_id(self, client):
        session = _create_session(client)
        data = client.get(f"/api/v1/agent/sessions/{session['session_id']}/records").get_json()
        assert TRACE_ID_PATTERN.match(data["traceId"])

    def test_capabilities_trace_id(self, client):
        data = client.get("/api/v1/agent/capabilities").get_json()
        assert TRACE_ID_PATTERN.match(data["traceId"])


# ========== POST /ask contract ==========

class TestAskContract:
    def test_response_fields_and_types(self, client):
        session = _create_session(client)
        data = client.post("/api/v1/agent/ask", json={
            "query": "test", "session_id": session["session_id"]
        }).get_json()
        assert isinstance(data["traceId"], str)
        assert isinstance(data["answer"], str)
        assert isinstance(data["llm_used"], bool)
        assert data["model"] is None or isinstance(data["model"], str)
        assert isinstance(data["response_time_ms"], int)
        assert isinstance(data["answer_source"], str)

    def test_answer_source_enum(self, client):
        session = _create_session(client)
        data = client.post("/api/v1/agent/ask", json={
            "query": "test", "session_id": session["session_id"]
        }).get_json()
        assert data["answer_source"] in ("copaw", "bailian", "demo")


# ========== POST /sessions contract ==========

class TestSessionContract:
    def test_response_fields_and_types(self, client):
        resp = client.post("/api/v1/agent/sessions", json={"title": "Test"})
        data = resp.get_json()
        assert isinstance(data["traceId"], str)
        assert isinstance(data["session_id"], str)
        assert isinstance(data["title"], str)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["query_count"], int)


# ========== GET /sessions contract ==========

class TestGetSessionsContract:
    def test_response_fields_and_types(self, client):
        data = client.get("/api/v1/agent/sessions").get_json()
        assert isinstance(data["traceId"], str)
        assert isinstance(data["sessions"], list)


# ========== DELETE /sessions contract ==========

class TestDeleteSessionContract:
    def test_response_fields_and_types(self, client):
        session = _create_session(client)
        data = client.delete(f"/api/v1/agent/sessions/{session['session_id']}").get_json()
        assert isinstance(data["traceId"], str)
        assert isinstance(data["message"], str)
        assert isinstance(data["deleted_records"], int)


# ========== GET /records contract ==========

class TestRecordsContract:
    def test_response_fields_and_types(self, client):
        session = _create_session(client)
        data = client.get(f"/api/v1/agent/sessions/{session['session_id']}/records").get_json()
        assert isinstance(data["traceId"], str)
        assert isinstance(data["session_id"], str)
        assert isinstance(data["records"], list)


# ========== GET /capabilities contract ==========

class TestCapabilitiesContract:
    def test_response_fields_and_types(self, client):
        data = client.get("/api/v1/agent/capabilities").get_json()
        assert isinstance(data["traceId"], str)
        assert isinstance(data["copaw_configured"], bool)
        assert isinstance(data["bailian_configured"], bool)
