"""Unit tests for Agent degradation logic."""
from unittest.mock import patch

from storage import Storage


class TestDegradation:
    def test_demo_fallback_when_no_providers(self, app, storage):
        from agent import CoPawAgent
        with app.app_context():
            # Create a session
            session = storage.create_session("test")
            agent = CoPawAgent(storage)

            with patch.dict("os.environ", {}, clear=True):
                result = agent.ask("test query", session["session_id"])

            assert result["answer_source"] == "demo"
            assert result["llm_used"] is False
            assert result["model"] is None
            assert "演示回答" in result["answer"]

    def test_copaw_used_when_available(self, app, storage):
        from agent import CoPawAgent
        with app.app_context():
            session = storage.create_session("test")
            agent = CoPawAgent(storage)

            with patch("copaw_bridge.is_available", return_value=True), \
                 patch("copaw_bridge.ask", return_value="CoPaw answer"):
                result = agent.ask("test", session["session_id"])

            assert result["answer_source"] == "copaw"
            assert result["llm_used"] is True
            assert result["answer"] == "CoPaw answer"

    def test_bailian_fallback_when_copaw_fails(self, app, storage):
        from agent import CoPawAgent
        with app.app_context():
            session = storage.create_session("test")
            agent = CoPawAgent(storage)

            with patch("copaw_bridge.is_available", return_value=True), \
                 patch("copaw_bridge.ask", return_value=None), \
                 patch("bailian_qa.is_available", return_value=True), \
                 patch("bailian_qa.ask", return_value="Bailian answer"):
                result = agent.ask("test", session["session_id"])

            assert result["answer_source"] == "bailian"
            assert result["llm_used"] is True
            assert result["answer"] == "Bailian answer"

    def test_demo_fallback_when_all_fail(self, app, storage):
        from agent import CoPawAgent
        with app.app_context():
            session = storage.create_session("test")
            agent = CoPawAgent(storage)

            with patch("copaw_bridge.is_available", return_value=True), \
                 patch("copaw_bridge.ask", return_value=None), \
                 patch("bailian_qa.is_available", return_value=True), \
                 patch("bailian_qa.ask", return_value=None):
                result = agent.ask("test", session["session_id"])

            assert result["answer_source"] == "demo"
            assert result["llm_used"] is False

    def test_auto_rename_on_first_question(self, app, storage):
        from agent import CoPawAgent
        with app.app_context():
            session = storage.create_session("新会话")
            agent = CoPawAgent(storage)

            query = "这是一个非常非常非常长的问题文本用来测试自动命名功能是否正确截断到二十个字符"
            with patch.dict("os.environ", {}, clear=True):
                agent.ask(query, session["session_id"])

            updated = storage.get_session_by_id(session["session_id"])
            assert updated["title"] == query[:20] + "..."

    def test_no_rename_on_second_question(self, app, storage):
        from agent import CoPawAgent
        with app.app_context():
            session = storage.create_session("新会话")
            agent = CoPawAgent(storage)

            with patch.dict("os.environ", {}, clear=True):
                agent.ask("第一个问题", session["session_id"])
                first_title = storage.get_session_by_id(session["session_id"])["title"]
                agent.ask("第二个问题不改名", session["session_id"])
                second_title = storage.get_session_by_id(session["session_id"])["title"]

            assert first_title == second_title
