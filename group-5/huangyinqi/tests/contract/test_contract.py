"""Contract tests - verify response schemas match API spec (09).
Covers TC-M01-006, 025, 026, 033, 058."""

import io
import pytest


class TestSessionsGetContract:
    """TC-M01-025: GET /sessions response schema."""

    def test_sessions_response_schema(self, client):
        client.post("/api/v1/agent/sessions", json={"title": "test"})
        res = client.get("/api/v1/agent/sessions")
        data = res.get_json()

        assert isinstance(data["traceId"], str)
        assert data["traceId"].startswith("tr_")
        assert isinstance(data["sessions"], list)
        assert isinstance(data["total"], int)

        s = data["sessions"][0]
        assert isinstance(s["id"], str)
        assert isinstance(s["title"], str)
        assert isinstance(s["created_at"], str)
        assert isinstance(s["updated_at"], str)
        assert isinstance(s["query_count"], int)


class TestSessionsPostContract:
    """TC-M01-026: POST /sessions response schema."""

    def test_create_session_response_schema(self, client):
        res = client.post("/api/v1/agent/sessions", json={"title": "contract test"})
        data = res.get_json()

        assert isinstance(data["traceId"], str)
        assert data["traceId"].startswith("tr_")
        assert isinstance(data["session_id"], str)
        assert isinstance(data["title"], str)
        assert isinstance(data["created_at"], str)
        assert isinstance(data["query_count"], int)
        assert data["query_count"] == 0


class TestAskContract:
    """TC-M01-006: POST /ask response schema."""

    def test_ask_response_schema(self, client):
        sid_res = client.post("/api/v1/agent/sessions", json={})
        sid = sid_res.get_json()["session_id"]

        res = client.post("/api/v1/agent/ask", json={"query": "test question", "session_id": sid})
        data = res.get_json()

        assert isinstance(data["traceId"], str)
        assert data["traceId"].startswith("tr_")
        assert isinstance(data["answer"], str)
        assert isinstance(data["llm_used"], bool)
        assert data["model"] is None or isinstance(data["model"], str)
        assert isinstance(data["response_time_ms"], int)
        assert data["answer_source"] in ("copaw", "bailian", "demo")
        assert isinstance(data["session_id"], str)
        assert isinstance(data["timestamp"], str)


class TestRecordsContract:
    """TC-M01-033: GET /sessions/<id>/records response schema."""

    def test_records_response_schema(self, client):
        sid_res = client.post("/api/v1/agent/sessions", json={})
        sid = sid_res.get_json()["session_id"]
        client.post("/api/v1/agent/ask", json={"query": "schema test", "session_id": sid})

        res = client.get(f"/api/v1/agent/sessions/{sid}/records")
        data = res.get_json()

        assert isinstance(data["traceId"], str)
        assert isinstance(data["session_id"], str)
        assert isinstance(data["records"], list)

        rec = data["records"][0]
        assert isinstance(rec["id"], str)
        assert isinstance(rec["query"], str)
        assert isinstance(rec["answer"], str)
        assert isinstance(rec["timestamp"], str)
        assert isinstance(rec["llm_used"], bool)
        assert isinstance(rec["answer_source"], str)
        assert rec["answer_source"] in ("copaw", "bailian", "demo")


class TestReportsContract:
    """TC-M01-058: Reports API response schema."""

    def _create_session(self, client):
        res = client.post("/api/v1/agent/sessions", json={})
        return res.get_json()["session_id"]

    def test_upload_report_response_schema(self, client):
        sid = self._create_session(client)
        html = b"<html><body><h1>Contract Test Report</h1></body></html>"
        res = client.post("/api/v1/agent/reports",
            data={"file": (io.BytesIO(html), "contract.html"), "session_id": sid},
            content_type="multipart/form-data")
        data = res.get_json()

        assert isinstance(data["traceId"], str)
        assert isinstance(data["report_id"], str)
        assert isinstance(data["title"], str)
        assert isinstance(data["rating"], str)
        assert isinstance(data["target_price"], str)
        assert isinstance(data["core_views"], list)
        assert isinstance(data["parsed_at"], str)
        assert data["status"] in ("parsing", "completed", "failed")

    def test_get_reports_response_schema(self, client):
        res = client.get("/api/v1/agent/reports")
        data = res.get_json()

        assert isinstance(data["traceId"], str)
        assert isinstance(data["reports"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["page_size"], int)

    def test_get_report_detail_schema(self, client):
        sid = self._create_session(client)
        html = b"<html><body><h1>Schema Detail</h1><p>content here</p></body></html>"
        upload_res = client.post("/api/v1/agent/reports",
            data={"file": (io.BytesIO(html), "schema.html"), "session_id": sid},
            content_type="multipart/form-data")
        rid = upload_res.get_json()["report_id"]

        res = client.get(f"/api/v1/agent/reports/{rid}")
        data = res.get_json()

        assert isinstance(data["traceId"], str)
        assert isinstance(data["report_id"], str)
        assert isinstance(data["title"], str)
        assert isinstance(data["rating"], str)
        assert isinstance(data["target_price"], str)
        assert isinstance(data["core_views"], list)
        assert isinstance(data["full_content"], str)
        assert isinstance(data["parsed_at"], str)
        assert isinstance(data["session_id"], str)

    def test_delete_report_schema(self, client):
        sid = self._create_session(client)
        html = b"<html><body><h1>Del Schema</h1></body></html>"
        upload_res = client.post("/api/v1/agent/reports",
            data={"file": (io.BytesIO(html), "del.html"), "session_id": sid},
            content_type="multipart/form-data")
        rid = upload_res.get_json()["report_id"]

        res = client.delete(f"/api/v1/agent/reports/{rid}")
        data = res.get_json()

        assert isinstance(data["traceId"], str)
        assert isinstance(data["deleted"], bool)
        assert data["deleted"] is True
        assert isinstance(data["report_id"], str)
