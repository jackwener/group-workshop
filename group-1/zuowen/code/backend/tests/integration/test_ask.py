"""
问答 API 集成测试 — 对齐 Spec 13 §3
覆盖 TC-M01-001 ~ TC-M01-004
"""


class TestAskSuccess:
    """TC-M01-001"""

    def test_ask_success_demo(self, client):
        """POST /ask → 200, Demo 模式"""
        # 先创建会话
        create_resp = client.post("/api/v1/agent/sessions", json={})
        sid = create_resp.get_json()["session_id"]

        resp = client.post("/api/v1/agent/ask", json={
            "query": "贵州茅台最新研报摘要",
            "session_id": sid,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert "answer" in data
        assert isinstance(data["llm_used"], bool)
        assert "response_time_ms" in data
        assert data["answer_source"] in ("copaw", "bailian", "demo")


class TestAskValidation:
    """TC-M01-002, TC-M01-003"""

    def test_ask_empty_query(self, client):
        """TC-M01-002: 空 query"""
        create_resp = client.post("/api/v1/agent/sessions", json={})
        sid = create_resp.get_json()["session_id"]

        resp = client.post("/api/v1/agent/ask", json={
            "query": "",
            "session_id": sid,
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "EMPTY_QUERY"

    def test_ask_long_query(self, client):
        """TC-M01-003: query > 500 字符"""
        create_resp = client.post("/api/v1/agent/sessions", json={})
        sid = create_resp.get_json()["session_id"]

        resp = client.post("/api/v1/agent/ask", json={
            "query": "x" * 501,
            "session_id": sid,
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_QUERY"

    def test_ask_missing_session(self, client):
        """session_id 不存在"""
        resp = client.post("/api/v1/agent/ask", json={
            "query": "测试问题",
            "session_id": "nonexistent-id",
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "SESSION_NOT_FOUND"


class TestFallback:
    """TC-M01-004"""

    def test_demo_fallback_no_api_key(self, client):
        """无 API Key → answer_source='demo'"""
        create_resp = client.post("/api/v1/agent/sessions", json={})
        sid = create_resp.get_json()["session_id"]

        resp = client.post("/api/v1/agent/ask", json={
            "query": "测试降级",
            "session_id": sid,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["answer_source"] == "demo"
        assert data["llm_used"] is False
