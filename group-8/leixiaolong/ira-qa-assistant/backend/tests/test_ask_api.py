"""S2 integration tests for POST /ask: TC-M01-001 ~ TC-M01-004"""
import uuid


class TestAskSuccess:
    def test_ask_demo_mode(self, client, seed_session):
        session_id = seed_session["session_id"]
        resp = client.post("/api/v1/agent/ask", json={
            "query": "半导体行业未来趋势如何？",
            "session_id": session_id,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["answer_source"] == "demo"
        assert data["llm_used"] is False
        assert data["model"] is None
        assert "answer" in data
        assert "response_time_ms" in data
        assert "traceId" in data

    def test_ask_auto_rename_first_question(self, client, seed_session):
        session_id = seed_session["session_id"]
        query_text = "这是一个非常长的测试问题用来验证自动命名功能是否正确工作"
        client.post("/api/v1/agent/ask", json={
            "query": query_text,
            "session_id": session_id,
        })
        # Check session title was auto-renamed
        resp = client.get("/api/v1/agent/sessions")
        sessions = resp.get_json()["sessions"]
        target = [s for s in sessions if s["session_id"] == session_id][0]
        assert target["title"] == query_text[:20] + "..."
        assert target["query_count"] == 1

    def test_ask_no_rename_on_second_question(self, client, seed_session):
        session_id = seed_session["session_id"]
        # First question
        client.post("/api/v1/agent/ask", json={
            "query": "第一个问题用于自动命名",
            "session_id": session_id,
        })
        # Get the title after first question
        resp = client.get("/api/v1/agent/sessions")
        first_title = [s for s in resp.get_json()["sessions"]
                       if s["session_id"] == session_id][0]["title"]

        # Second question
        client.post("/api/v1/agent/ask", json={
            "query": "第二个问题不应该改变标题",
            "session_id": session_id,
        })
        resp2 = client.get("/api/v1/agent/sessions")
        second_title = [s for s in resp2.get_json()["sessions"]
                        if s["session_id"] == session_id][0]["title"]
        assert first_title == second_title


class TestAskValidation:
    def test_ask_empty_query(self, client, seed_session):
        resp = client.post("/api/v1/agent/ask", json={
            "query": "",
            "session_id": seed_session["session_id"],
        })
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "EMPTY_QUERY"

    def test_ask_whitespace_query(self, client, seed_session):
        resp = client.post("/api/v1/agent/ask", json={
            "query": "   ",
            "session_id": seed_session["session_id"],
        })
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "EMPTY_QUERY"

    def test_ask_long_query(self, client, seed_session):
        resp = client.post("/api/v1/agent/ask", json={
            "query": "x" * 501,
            "session_id": seed_session["session_id"],
        })
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_QUERY"

    def test_ask_invalid_session_id(self, client):
        resp = client.post("/api/v1/agent/ask", json={
            "query": "test",
            "session_id": "not-a-uuid",
        })
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_SESSION_ID"

    def test_ask_session_not_found(self, client):
        fake_id = str(uuid.uuid4())
        resp = client.post("/api/v1/agent/ask", json={
            "query": "test",
            "session_id": fake_id,
        })
        assert resp.status_code == 404
        assert resp.get_json()["error"]["code"] == "SESSION_NOT_FOUND"
