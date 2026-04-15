import os
import shutil
import time
import pytest
from backend.storage import Storage

TEST_DIR = os.path.join(os.path.dirname(__file__), "..", "test_data")


@pytest.fixture(autouse=True)
def clean_test_dir():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)


def make_storage():
    return Storage(data_dir=TEST_DIR)


# ========== TC-M01-040: Storage.__init__ ==========

class TestStorageInit:
    def test_creates_directory_if_not_exists(self):
        assert not os.path.exists(TEST_DIR)
        s = make_storage()
        assert os.path.isdir(TEST_DIR)
        assert os.path.isfile(s.sessions_file)
        assert os.path.isfile(s.records_file)

    def test_init_files_contain_empty_list(self):
        s = make_storage()
        assert s._read_json(s.sessions_file) == []
        assert s._read_json(s.records_file) == []


# ========== TC-M01-041: create_session ==========

class TestCreateSession:
    def test_returns_dict_with_5_fields(self):
        s = make_storage()
        result = s.create_session("sess-1", "Test Session")
        assert isinstance(result, dict)
        assert set(result.keys()) == {"session_id", "title", "created_at", "updated_at", "query_count"}
        assert result["session_id"] == "sess-1"
        assert result["title"] == "Test Session"
        assert result["query_count"] == 0

    def test_default_title(self):
        s = make_storage()
        result = s.create_session("sess-2")
        assert result["title"] == "新会话"

    def test_title_too_long_raises(self):
        s = make_storage()
        with pytest.raises(ValueError, match="INVALID_SESSION_TITLE"):
            s.create_session("sess-3", "x" * 101)

    def test_persists_to_json(self):
        s = make_storage()
        s.create_session("sess-4", "Persisted")
        sessions = s._read_json(s.sessions_file)
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "sess-4"


# ========== TC-M01-042: get_sessions ==========

class TestGetSessions:
    def test_returns_list_ordered_by_created_at_desc(self):
        s = make_storage()
        s.create_session("s1", "First")
        time.sleep(0.01)
        s.create_session("s2", "Second")
        result = s.get_sessions()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["session_id"] == "s2"
        assert result[1]["session_id"] == "s1"

    def test_empty_returns_empty_list(self):
        s = make_storage()
        assert s.get_sessions() == []


# ========== TC-M01-043: delete_session ==========

class TestDeleteSession:
    def test_removes_session_and_returns_cascade_count(self):
        s = make_storage()
        s.create_session("s1", "ToDelete")
        s.add_record("s1", "q1", "a1", False, None, 100, "demo")
        s.add_record("s1", "q2", "a2", False, None, 200, "demo")
        deleted = s.delete_session("s1")
        assert deleted == 2
        assert s.get_session("s1") is None
        assert s.get_records_by_session("s1") == []

    def test_delete_nonexistent_returns_zero(self):
        s = make_storage()
        deleted = s.delete_session("nonexistent")
        assert deleted == 0


# ========== TC-M01-046: update_session ==========

class TestUpdateSession:
    def test_updates_title_and_updated_at(self):
        s = make_storage()
        original = s.create_session("s1", "Original")
        time.sleep(0.01)
        updated = s.update_session("s1", "Updated Title")
        assert updated["title"] == "Updated Title"
        assert updated["updated_at"] > original["updated_at"]

    def test_not_found_raises_keyerror(self):
        s = make_storage()
        with pytest.raises(KeyError):
            s.update_session("nonexistent", "Title")

    def test_title_too_long_raises(self):
        s = make_storage()
        s.create_session("s1", "Ok")
        with pytest.raises(ValueError, match="INVALID_SESSION_TITLE"):
            s.update_session("s1", "x" * 101)


# ========== TC-M01-044: add_record ==========

class TestAddRecord:
    def test_returns_dict_with_9_fields(self):
        s = make_storage()
        s.create_session("s1")
        rec = s.add_record("s1", "Hello?", "World!", True, "qwen", 123, "bailian")
        assert isinstance(rec, dict)
        assert set(rec.keys()) == {
            "record_id", "session_id", "query", "answer",
            "llm_used", "model", "response_time_ms", "answer_source", "timestamp"
        }
        assert rec["record_id"].startswith("rec_")

    def test_increments_query_count(self):
        s = make_storage()
        s.create_session("s1")
        s.add_record("s1", "q1", "a1", False, None, 100, "demo")
        session = s.get_session("s1")
        assert session["query_count"] == 1

    def test_auto_rename_on_first_query(self):
        s = make_storage()
        s.create_session("s1", "新会话")
        s.add_record("s1", "这是一个很长的问题用来测试自动命名功能", "answer", False, None, 100, "demo")
        session = s.get_session("s1")
        assert session["title"] == "这是一个很长的问题用来测试自动命名功能"[:20] + "..."


# ========== TC-M01-045: get_records_by_session ==========

class TestGetRecordsBySession:
    def test_filters_and_orders_by_timestamp(self):
        s = make_storage()
        s.create_session("s1")
        s.create_session("s2")
        s.add_record("s1", "q1", "a1", False, None, 100, "demo")
        time.sleep(0.01)
        s.add_record("s2", "q2", "a2", False, None, 100, "demo")
        time.sleep(0.01)
        s.add_record("s1", "q3", "a3", False, None, 100, "demo")
        records = s.get_records_by_session("s1")
        assert len(records) == 2
        assert records[0]["query"] == "q1"
        assert records[1]["query"] == "q3"

    def test_empty_session_returns_empty_list(self):
        s = make_storage()
        s.create_session("s1")
        assert s.get_records_by_session("s1") == []


# ========== TC-M01-047: delete_records_by_session ==========

class TestDeleteRecordsBySession:
    def test_returns_deleted_count(self):
        s = make_storage()
        s.create_session("s1")
        s.add_record("s1", "q1", "a1", False, None, 100, "demo")
        s.add_record("s1", "q2", "a2", False, None, 100, "demo")
        count = s.delete_records_by_session("s1")
        assert count == 2
        assert s.get_records_by_session("s1") == []

    def test_no_matching_returns_zero(self):
        s = make_storage()
        assert s.delete_records_by_session("nonexistent") == 0
