"""Unit tests for Storage class - Sessions, Records, Reports.
Covers TC-M01-040~051."""

import time
import pytest


class TestStorageInit:
    """TC-M01-040: Storage initialization."""

    def test_init_creates_directory(self, storage):
        """Data directory is created automatically."""
        import os
        assert os.path.isdir(storage.data_dir)

    def test_init_creates_json_files(self, storage):
        """All three JSON files are initialized."""
        import os
        assert os.path.exists(storage.sessions_file)
        assert os.path.exists(storage.records_file)
        assert os.path.exists(storage.reports_file)

    def test_init_files_are_empty_arrays(self, storage):
        """JSON files are initialized with empty arrays."""
        sessions = storage._read_json(storage.sessions_file)
        records = storage._read_json(storage.records_file)
        reports = storage._read_json(storage.reports_file)
        assert sessions == []
        assert records == []
        assert reports == []


class TestCreateSession:
    """TC-M01-041: create_session."""

    def test_create_session_returns_dict_with_5_fields(self, storage):
        session = storage.create_session("s1", "测试会话")
        assert isinstance(session, dict)
        assert set(session.keys()) == {"session_id", "title", "created_at", "updated_at", "query_count"}

    def test_create_session_default_title(self, storage):
        session = storage.create_session("s2")
        assert session["title"] == "新会话"

    def test_create_session_query_count_zero(self, storage):
        session = storage.create_session("s3", "abc")
        assert session["query_count"] == 0

    def test_create_session_iso8601_format(self, storage):
        session = storage.create_session("s4")
        assert session["created_at"].endswith("Z")
        assert "T" in session["created_at"]

    def test_create_session_persists(self, storage):
        storage.create_session("s5", "持久化测试")
        sessions = storage.get_sessions()
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "s5"


class TestGetSessions:
    """TC-M01-042: get_sessions."""

    def test_get_sessions_empty(self, storage):
        assert storage.get_sessions() == []

    def test_get_sessions_sorted_by_updated_at(self, storage):
        storage.create_session("s1", "first")
        time.sleep(0.01)
        storage.create_session("s2", "second")
        sessions = storage.get_sessions()
        assert sessions[0]["session_id"] == "s2"
        assert sessions[1]["session_id"] == "s1"


class TestDeleteSession:
    """TC-M01-043: delete_session with cascade."""

    def test_delete_session_removes_session(self, storage):
        storage.create_session("s1", "test")
        storage.delete_session("s1")
        assert storage.get_sessions() == []

    def test_delete_session_cascade_deletes_records(self, storage):
        storage.create_session("s1", "test")
        storage.add_record("s1", "q1", "a1", False, None, 100, "demo")
        storage.add_record("s1", "q2", "a2", False, None, 100, "demo")
        storage.delete_session("s1")
        assert storage.get_records_by_session("s1") == []

    def test_delete_nonexistent_session(self, storage):
        # Should not raise
        storage.delete_session("nonexistent")


class TestUpdateSession:
    """TC-M01-046: update_session."""

    def test_update_session_title(self, storage):
        storage.create_session("s1", "old")
        updated = storage.update_session("s1", title="new")
        assert updated["title"] == "new"
        assert updated["session_id"] == "s1"

    def test_update_session_returns_full_dict(self, storage):
        storage.create_session("s1", "test")
        updated = storage.update_session("s1", query_count=5)
        assert "session_id" in updated
        assert "title" in updated
        assert "created_at" in updated
        assert "updated_at" in updated
        assert updated["query_count"] == 5

    def test_update_nonexistent_session(self, storage):
        result = storage.update_session("nonexistent", title="x")
        assert result is None


class TestDeleteRecordsBySession:
    """TC-M01-047: delete_records_by_session."""

    def test_delete_records_returns_count(self, storage):
        storage.create_session("s1", "test")
        storage.add_record("s1", "q1", "a1", False, None, 100, "demo")
        storage.add_record("s1", "q2", "a2", False, None, 100, "demo")
        deleted = storage.delete_records_by_session("s1")
        assert deleted == 2

    def test_delete_records_no_records(self, storage):
        deleted = storage.delete_records_by_session("nonexistent")
        assert deleted == 0

    def test_delete_records_preserves_other_sessions(self, storage):
        storage.create_session("s1", "one")
        storage.create_session("s2", "two")
        storage.add_record("s1", "q1", "a1", False, None, 100, "demo")
        storage.add_record("s2", "q2", "a2", False, None, 100, "demo")
        storage.delete_records_by_session("s1")
        assert len(storage.get_records_by_session("s2")) == 1


class TestAddRecord:
    """TC-M01-044: add_record."""

    def test_add_record_returns_full_dict(self, storage):
        storage.create_session("s1", "test")
        record = storage.add_record("s1", "hello", "world", True, "qwen", 500, "bailian")
        assert record["session_id"] == "s1"
        assert record["query"] == "hello"
        assert record["answer"] == "world"
        assert record["llm_used"] is True
        assert record["model"] == "qwen"
        assert record["response_time_ms"] == 500
        assert record["answer_source"] == "bailian"
        assert record["id"].startswith("rec_")

    def test_add_record_increments_query_count(self, storage):
        storage.create_session("s1", "test")
        storage.add_record("s1", "q1", "a1", False, None, 100, "demo")
        session = storage.get_session_by_id("s1")
        assert session["query_count"] == 1

    def test_add_record_auto_names_on_first_query(self, storage):
        storage.create_session("s1", "新会话")
        long_query = "这是一个非常长的测试问题内容，用来验证首次提问的自动命名功能"
        storage.add_record("s1", long_query, "answer", False, None, 100, "demo")
        session = storage.get_session_by_id("s1")
        assert session["title"] == long_query[:20] + "..."

    def test_add_record_no_rename_after_first(self, storage):
        storage.create_session("s1", "新会话")
        storage.add_record("s1", "first question", "a1", False, None, 100, "demo")
        first_title = storage.get_session_by_id("s1")["title"]
        storage.add_record("s1", "second question", "a2", False, None, 100, "demo")
        second_title = storage.get_session_by_id("s1")["title"]
        assert first_title == second_title


class TestGetRecordsBySession:
    """TC-M01-045: get_records_by_session."""

    def test_get_records_empty(self, storage):
        assert storage.get_records_by_session("nonexistent") == []

    def test_get_records_filters_by_session(self, storage):
        storage.create_session("s1", "one")
        storage.create_session("s2", "two")
        storage.add_record("s1", "q1", "a1", False, None, 100, "demo")
        storage.add_record("s2", "q2", "a2", False, None, 100, "demo")
        records = storage.get_records_by_session("s1")
        assert len(records) == 1
        assert records[0]["query"] == "q1"


class TestCreateReport:
    """TC-M01-048: create_report."""

    def test_create_report_returns_full_dict(self, storage):
        file_data = {
            "title": "测试研报",
            "rating": "买入",
            "target_price": "100元",
            "core_views": ["观点1", "观点2"],
            "full_content": "完整内容",
            "file_path": "/tmp/test.pdf",
        }
        report = storage.create_report("r1", "s1", file_data)
        assert report["report_id"] == "r1"
        assert report["session_id"] == "s1"
        assert report["title"] == "测试研报"
        assert report["status"] == "parsing"
        assert report["parsed_at"].endswith("Z")


class TestGetReports:
    """TC-M01-049: get_reports."""

    def test_get_reports_empty(self, storage):
        result = storage.get_reports()
        assert result["reports"] == []
        assert result["total"] == 0

    def test_get_reports_keyword_search(self, storage):
        storage.create_report("r1", "s1", {"title": "贵州茅台深度研报", "rating": "买入", "target_price": "2000元", "core_views": [], "full_content": "", "file_path": ""})
        storage.create_report("r2", "s1", {"title": "比亚迪分析报告", "rating": "增持", "target_price": "300元", "core_views": [], "full_content": "", "file_path": ""})

        result = storage.get_reports(keyword="茅台")
        assert result["total"] == 1
        assert result["reports"][0]["title"] == "贵州茅台深度研报"

    def test_get_reports_pagination(self, storage):
        for i in range(5):
            storage.create_report(f"r{i}", "s1", {"title": f"报告{i}", "rating": "", "target_price": "", "core_views": [], "full_content": "", "file_path": ""})
        result = storage.get_reports(page=1, page_size=2)
        assert len(result["reports"]) == 2
        assert result["total"] == 5
        assert result["page"] == 1


class TestGetReportById:
    """TC-M01-050: get_report_by_id."""

    def test_get_report_by_id_found(self, storage):
        storage.create_report("r1", "s1", {"title": "Test", "rating": "", "target_price": "", "core_views": [], "full_content": "Full", "file_path": ""})
        report = storage.get_report_by_id("r1")
        assert report is not None
        assert report["title"] == "Test"
        assert report["full_content"] == "Full"

    def test_get_report_by_id_not_found(self, storage):
        assert storage.get_report_by_id("nonexistent") is None


class TestDeleteReport:
    """TC-M01-051: delete_report."""

    def test_delete_report_success(self, storage):
        storage.create_report("r1", "s1", {"title": "Test", "rating": "", "target_price": "", "core_views": [], "full_content": "", "file_path": ""})
        assert storage.delete_report("r1") is True
        assert storage.get_report_by_id("r1") is None

    def test_delete_report_not_found(self, storage):
        assert storage.delete_report("nonexistent") is False
