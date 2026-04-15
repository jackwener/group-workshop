import json
import os
import uuid
from datetime import datetime, timezone


class Storage:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.records_file = os.path.join(data_dir, "qa_records.json")
        self.uploads_file = os.path.join(data_dir, "upload_files.json")
        self.reports_file = os.path.join(data_dir, "reports.json")

    def _read(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write(self, filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _now_iso():
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def is_valid_uuid(value):
        try:
            uuid.UUID(str(value))
            return True
        except (ValueError, AttributeError):
            return False

    # ─── Session CRUD ──────────────────────────────────────────

    def create_session(self, title="新会话"):
        sessions = self._read(self.sessions_file)
        now = self._now_iso()
        session = {
            "session_id": str(uuid.uuid4()),
            "title": title,
            "created_at": now,
            "updated_at": now,
            "query_count": 0,
        }
        sessions.append(session)
        self._write(self.sessions_file, sessions)
        return session

    def get_sessions(self):
        sessions = self._read(self.sessions_file)
        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        return sessions

    def get_session_by_id(self, session_id):
        sessions = self._read(self.sessions_file)
        for s in sessions:
            if s["session_id"] == session_id:
                return s
        return None

    def delete_session(self, session_id):
        sessions = self._read(self.sessions_file)
        new_sessions = [s for s in sessions if s["session_id"] != session_id]
        if len(new_sessions) == len(sessions):
            return False
        self._write(self.sessions_file, new_sessions)
        self.delete_records_by_session(session_id)
        self.delete_uploads_by_session(session_id)
        return True

    def update_session_title(self, session_id, title):
        sessions = self._read(self.sessions_file)
        for s in sessions:
            if s["session_id"] == session_id:
                s["title"] = title
                s["updated_at"] = self._now_iso()
                self._write(self.sessions_file, sessions)
                return s
        return None

    # ─── QARecord CRUD ─────────────────────────────────────────

    def add_record(self, session_id, query, answer, llm_used, model,
                   response_time_ms, answer_source, sources=None):
        records = self._read(self.records_file)
        record = {
            "record_id": f"rec_{uuid.uuid4().hex}",
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_used": llm_used,
            "model": model,
            "response_time_ms": response_time_ms,
            "answer_source": answer_source,
            "timestamp": self._now_iso(),
            "sources": sources or [],
        }
        records.append(record)
        self._write(self.records_file, records)

        # 更新 session 的 query_count 和 updated_at
        sessions = self._read(self.sessions_file)
        for s in sessions:
            if s["session_id"] == session_id:
                s["query_count"] = s.get("query_count", 0) + 1
                s["updated_at"] = self._now_iso()
                self._write(self.sessions_file, sessions)
                break

        return record

    def get_records_by_session(self, session_id):
        records = self._read(self.records_file)
        filtered = [r for r in records if r["session_id"] == session_id]
        filtered.sort(key=lambda r: r["timestamp"])
        return filtered

    def delete_records_by_session(self, session_id):
        records = self._read(self.records_file)
        new_records = [r for r in records if r["session_id"] != session_id]
        self._write(self.records_file, new_records)

    # ─── UploadFile helpers (级联删除用) ────────────────────────

    def delete_uploads_by_session(self, session_id):
        uploads = self._read(self.uploads_file)
        new_uploads = [u for u in uploads if u["session_id"] != session_id]
        self._write(self.uploads_file, new_uploads)
