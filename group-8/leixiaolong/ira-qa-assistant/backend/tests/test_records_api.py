"""S2 integration tests for GET /sessions/<id>/records: TC-M01-030 ~ TC-M01-033"""
import uuid


class TestGetRecords:
    def test_get_records_with_data(self, client, seed_session):
        session_id = seed_session["session_id"]
        # Submit a question first
        client.post("/api/v1/agent/ask", json={
            "query": "测试问题",
            "session_id": session_id,
        })
        resp = client.get(f"/api/v1/agent/sessions/{session_id}/records")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        records = data["records"]
        assert len(records) == 1
        record = records[0]
        assert record["query"] == "测试问题"
        assert "answer" in record
        assert "record_id" in record
        assert "answer_source" in record
        assert "llm_used" in record
        assert "response_time_ms" in record
        assert "timestamp" in record

    def test_get_records_empty(self, client, seed_session):
        session_id = seed_session["session_id"]
        resp = client.get(f"/api/v1/agent/sessions/{session_id}/records")
        assert resp.status_code == 200
        assert resp.get_json()["records"] == []

    def test_get_records_invalid_session_id(self, client):
        resp = client.get("/api/v1/agent/sessions/bad-id/records")
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_SESSION_ID"

    def test_get_records_session_not_found(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/api/v1/agent/sessions/{fake_id}/records")
        assert resp.status_code == 404
        assert resp.get_json()["error"]["code"] == "SESSION_NOT_FOUND"
