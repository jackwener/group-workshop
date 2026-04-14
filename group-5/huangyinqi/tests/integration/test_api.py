"""Integration tests for all API endpoints.
Covers TC-M01-001~005, TC-M01-020~024, TC-M01-030~032, TC-M01-050~057."""

import io
import json
import pytest


# ── Session API Tests (TC-M01-020~024) ──

class TestGetSessions:
    """TC-M01-020: GET /sessions."""

    def test_get_sessions_empty(self, client):
        res = client.get("/api/v1/agent/sessions")
        assert res.status_code == 200
        data = res.get_json()
        assert data["sessions"] == []
        assert data["total"] == 0
        assert "traceId" in data

    def test_get_sessions_with_data(self, client):
        client.post("/api/v1/agent/sessions", json={"title": "s1"})
        client.post("/api/v1/agent/sessions", json={"title": "s2"})
        res = client.get("/api/v1/agent/sessions")
        data = res.get_json()
        assert data["total"] == 2
        assert len(data["sessions"]) == 2


class TestPostSessions:
    """TC-M01-021, 022: POST /sessions."""

    def test_create_session_default_title(self, client):
        res = client.post("/api/v1/agent/sessions", json={})
        assert res.status_code == 201
        data = res.get_json()
        assert data["title"] == "新会话"
        assert "session_id" in data
        assert "created_at" in data
        assert data["query_count"] == 0
        assert "traceId" in data

    def test_create_session_custom_title(self, client):
        res = client.post("/api/v1/agent/sessions", json={"title": "自定义标题"})
        assert res.status_code == 201
        assert res.get_json()["title"] == "自定义标题"

    def test_create_session_title_too_long(self, client):
        res = client.post("/api/v1/agent/sessions", json={"title": "x" * 101})
        assert res.status_code == 400
        assert res.get_json()["error"]["code"] == "INVALID_TITLE"


class TestDeleteSessions:
    """TC-M01-023, 024: DELETE /sessions/<id>."""

    def test_delete_session_success(self, client):
        create_res = client.post("/api/v1/agent/sessions", json={"title": "to delete"})
        sid = create_res.get_json()["session_id"]
        res = client.delete(f"/api/v1/agent/sessions/{sid}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["deleted"] is True
        assert data["session_id"] == sid

    def test_delete_session_not_found(self, client):
        res = client.delete("/api/v1/agent/sessions/nonexistent-id")
        assert res.status_code == 404
        assert res.get_json()["error"]["code"] == "NOT_FOUND"

    def test_delete_session_cascade(self, client):
        # Create session
        create_res = client.post("/api/v1/agent/sessions", json={})
        sid = create_res.get_json()["session_id"]
        # Add a question
        client.post("/api/v1/agent/ask", json={"query": "test question", "session_id": sid})
        # Delete session
        client.delete(f"/api/v1/agent/sessions/{sid}")
        # Verify records are gone (session also gone, returns 404)
        res = client.get(f"/api/v1/agent/sessions/{sid}/records")
        assert res.status_code == 404


# ── Ask API Tests (TC-M01-001~005) ──

class TestPostAsk:
    """TC-M01-001~005: POST /ask."""

    def _create_session(self, client):
        res = client.post("/api/v1/agent/sessions", json={})
        return res.get_json()["session_id"]

    def test_ask_success_demo_mode(self, client):
        sid = self._create_session(client)
        res = client.post("/api/v1/agent/ask", json={"query": "hello", "session_id": sid})
        assert res.status_code == 200
        data = res.get_json()
        assert "answer" in data
        assert data["answer_source"] == "demo"
        assert data["llm_used"] is False
        assert data["session_id"] == sid
        assert "timestamp" in data
        assert "traceId" in data

    def test_ask_empty_query(self, client):
        sid = self._create_session(client)
        res = client.post("/api/v1/agent/ask", json={"query": "", "session_id": sid})
        assert res.status_code == 400
        assert res.get_json()["error"]["code"] == "EMPTY_QUERY"

    def test_ask_whitespace_query(self, client):
        sid = self._create_session(client)
        res = client.post("/api/v1/agent/ask", json={"query": "   ", "session_id": sid})
        assert res.status_code == 400
        assert res.get_json()["error"]["code"] == "EMPTY_QUERY"

    def test_ask_query_too_long(self, client):
        sid = self._create_session(client)
        res = client.post("/api/v1/agent/ask", json={"query": "x" * 501, "session_id": sid})
        assert res.status_code == 400
        assert res.get_json()["error"]["code"] == "INVALID_QUERY"

    def test_ask_invalid_session(self, client):
        res = client.post("/api/v1/agent/ask", json={"query": "hello", "session_id": "invalid"})
        assert res.status_code == 400
        assert res.get_json()["error"]["code"] == "INVALID_SESSION"


# ── Records API Tests (TC-M01-030~032) ──

class TestGetRecords:
    """TC-M01-030~032: GET /sessions/<id>/records."""

    def _create_session(self, client):
        res = client.post("/api/v1/agent/sessions", json={})
        return res.get_json()["session_id"]

    def test_get_records_success(self, client):
        sid = self._create_session(client)
        client.post("/api/v1/agent/ask", json={"query": "test", "session_id": sid})
        res = client.get(f"/api/v1/agent/sessions/{sid}/records")
        assert res.status_code == 200
        data = res.get_json()
        assert data["session_id"] == sid
        assert len(data["records"]) == 1
        rec = data["records"][0]
        assert "id" in rec
        assert rec["query"] == "test"
        assert "answer" in rec
        assert "timestamp" in rec
        assert "llm_used" in rec
        assert "answer_source" in rec

    def test_get_records_empty(self, client):
        sid = self._create_session(client)
        res = client.get(f"/api/v1/agent/sessions/{sid}/records")
        data = res.get_json()
        assert data["records"] == []

    def test_get_records_invalid_session(self, client):
        res = client.get("/api/v1/agent/sessions/invalid/records")
        assert res.status_code == 404
        assert res.get_json()["error"]["code"] == "NOT_FOUND"


# ── Capabilities API Test ──

class TestGetCapabilities:
    """TC-M01-001: GET /capabilities."""

    def test_capabilities_no_config(self, client):
        res = client.get("/api/v1/agent/capabilities")
        assert res.status_code == 200
        data = res.get_json()
        assert "copaw_configured" in data
        assert "bailian_configured" in data
        assert "traceId" in data


# ── Report API Tests (TC-M01-050~057) ──

class TestPostReports:
    """TC-M01-050~053: POST /reports."""

    def _create_session(self, client):
        res = client.post("/api/v1/agent/sessions", json={})
        return res.get_json()["session_id"]

    def test_upload_html_report(self, client):
        sid = self._create_session(client)
        html_content = b"<html><body><h1>Test Report</h1><p>Rating: Buy, target price: 100</p></body></html>"
        data = {
            "file": (io.BytesIO(html_content), "test.html"),
            "session_id": sid,
        }
        res = client.post("/api/v1/agent/reports", data=data, content_type="multipart/form-data")
        assert res.status_code == 201
        result = res.get_json()
        assert "report_id" in result
        assert "title" in result
        assert "status" in result
        assert "traceId" in result

    def test_upload_invalid_format(self, client):
        sid = self._create_session(client)
        data = {
            "file": (io.BytesIO(b"text"), "test.txt"),
            "session_id": sid,
        }
        res = client.post("/api/v1/agent/reports", data=data, content_type="multipart/form-data")
        assert res.status_code == 400
        assert res.get_json()["error"]["code"] == "INVALID_FILE_FORMAT"

    def test_upload_no_file(self, client):
        sid = self._create_session(client)
        data = {"session_id": sid}
        res = client.post("/api/v1/agent/reports", data=data, content_type="multipart/form-data")
        assert res.status_code == 400

    def test_upload_invalid_session(self, client):
        data = {
            "file": (io.BytesIO(b"<html></html>"), "test.html"),
            "session_id": "invalid-session",
        }
        res = client.post("/api/v1/agent/reports", data=data, content_type="multipart/form-data")
        assert res.status_code == 400


class TestGetReports:
    """TC-M01-054, 055: GET /reports."""

    def _create_session(self, client):
        res = client.post("/api/v1/agent/sessions", json={})
        return res.get_json()["session_id"]

    def _upload_report(self, client, sid, title="test"):
        html = f"<html><body><h1>{title}</h1></body></html>".encode()
        data = {
            "file": (io.BytesIO(html), f"{title}.html"),
            "session_id": sid,
        }
        return client.post("/api/v1/agent/reports", data=data, content_type="multipart/form-data")

    def test_get_reports_empty(self, client):
        res = client.get("/api/v1/agent/reports")
        assert res.status_code == 200
        data = res.get_json()
        assert data["reports"] == []
        assert data["total"] == 0

    def test_get_reports_with_data(self, client):
        sid = self._create_session(client)
        self._upload_report(client, sid, "report1")
        res = client.get("/api/v1/agent/reports")
        data = res.get_json()
        assert data["total"] >= 1

    def test_get_reports_search(self, client):
        sid = self._create_session(client)
        self._upload_report(client, sid, "贵州茅台")
        self._upload_report(client, sid, "比亚迪")
        res = client.get("/api/v1/agent/reports?keyword=茅台")
        data = res.get_json()
        assert data["total"] >= 1


class TestGetReportById:
    """TC-M01-056: GET /reports/<id>."""

    def test_get_report_not_found(self, client):
        res = client.get("/api/v1/agent/reports/nonexistent")
        assert res.status_code == 404
        assert res.get_json()["error"]["code"] == "NOT_FOUND"

    def test_get_report_success(self, client):
        sid_res = client.post("/api/v1/agent/sessions", json={})
        sid = sid_res.get_json()["session_id"]
        html = b"<html><body><h1>Detail Report</h1><p>full content here</p></body></html>"
        upload_res = client.post("/api/v1/agent/reports",
            data={"file": (io.BytesIO(html), "detail.html"), "session_id": sid},
            content_type="multipart/form-data")
        rid = upload_res.get_json()["report_id"]

        res = client.get(f"/api/v1/agent/reports/{rid}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["report_id"] == rid
        assert "full_content" in data
        assert "session_id" in data


class TestDeleteReport:
    """TC-M01-057: DELETE /reports/<id>."""

    def test_delete_report_not_found(self, client):
        res = client.delete("/api/v1/agent/reports/nonexistent")
        assert res.status_code == 404

    def test_delete_report_success(self, client):
        sid_res = client.post("/api/v1/agent/sessions", json={})
        sid = sid_res.get_json()["session_id"]
        html = b"<html><body><h1>To Delete</h1></body></html>"
        upload_res = client.post("/api/v1/agent/reports",
            data={"file": (io.BytesIO(html), "delete.html"), "session_id": sid},
            content_type="multipart/form-data")
        rid = upload_res.get_json()["report_id"]

        res = client.delete(f"/api/v1/agent/reports/{rid}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["deleted"] is True

        # Verify deleted
        res2 = client.get(f"/api/v1/agent/reports/{rid}")
        assert res2.status_code == 404
