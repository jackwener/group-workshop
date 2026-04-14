"""
问答记录 API 集成测试 — 对齐 Spec 13 §3.2
覆盖 TC-M01-030 ~ TC-M01-031
"""


class TestGetRecords:
    """TC-M01-030"""

    def test_get_records_success(self, client):
        """有记录的会话"""
        # 创建会话
        create_resp = client.post("/api/v1/agent/sessions", json={})
        sid = create_resp.get_json()["session_id"]

        # 提问
        client.post("/api/v1/agent/ask", json={
            "query": "茅台研报",
            "session_id": sid,
        })

        # 获取记录
        resp = client.get(f"/api/v1/agent/sessions/{sid}/records")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert len(data["records"]) == 1
        record = data["records"][0]
        assert "id" in record
        assert record["query"] == "茅台研报"
        assert "answer" in record
        assert "llm_used" in record
        assert "answer_source" in record
        assert "timestamp" in record

    def test_get_records_empty(self, client):
        """空记录的会话"""
        create_resp = client.post("/api/v1/agent/sessions", json={})
        sid = create_resp.get_json()["session_id"]

        resp = client.get(f"/api/v1/agent/sessions/{sid}/records")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["records"] == []


class TestGetRecordsNotFound:
    """TC-M01-031"""

    def test_records_session_not_found(self, client):
        """不存在的会话"""
        resp = client.get("/api/v1/agent/sessions/nonexistent-id/records")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "SESSION_NOT_FOUND"
