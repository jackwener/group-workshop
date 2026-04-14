import json
import os
import time
from datetime import datetime, timezone


class Storage:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.records_file = os.path.join(data_dir, "qa_records.json")
        if not os.path.exists(self.sessions_file):
            self._write_json(self.sessions_file, [])
        if not os.path.exists(self.records_file):
            self._write_json(self.records_file, [])

    def _read_json(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ========== Session CRUD ==========

    def create_session(self, session_id, title="新会话"):
        if len(title) > 100:
            raise ValueError("INVALID_SESSION_TITLE")
        now = datetime.now(timezone.utc).isoformat()
        session = {
            "session_id": session_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "query_count": 0,
        }
        sessions = self._read_json(self.sessions_file)
        sessions.append(session)
        self._write_json(self.sessions_file, sessions)
        return session

    def get_sessions(self):
        sessions = self._read_json(self.sessions_file)
        sessions.sort(key=lambda s: s["created_at"], reverse=True)
        return sessions

    def delete_session(self, session_id):
        deleted_records = self.delete_records_by_session(session_id)
        sessions = self._read_json(self.sessions_file)
        sessions = [s for s in sessions if s["session_id"] != session_id]
        self._write_json(self.sessions_file, sessions)
        return deleted_records

    def update_session(self, session_id, title):
        if len(title) > 100:
            raise ValueError("INVALID_SESSION_TITLE")
        sessions = self._read_json(self.sessions_file)
        found = False
        for s in sessions:
            if s["session_id"] == session_id:
                s["title"] = title
                s["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._write_json(self.sessions_file, sessions)
                found = True
                return s
        if not found:
            raise KeyError(f"Session {session_id} not found")

    def get_session(self, session_id):
        sessions = self._read_json(self.sessions_file)
        for s in sessions:
            if s["session_id"] == session_id:
                return s
        return None

    # ========== QARecord CRUD ==========

    def add_record(self, session_id, query, answer, llm_used, model,
                   response_time_ms, answer_source):
        record_id = f"rec_{int(time.time() * 1000)}"
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "record_id": record_id,
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_used": llm_used,
            "model": model,
            "response_time_ms": response_time_ms,
            "answer_source": answer_source,
            "timestamp": now,
        }
        records = self._read_json(self.records_file)
        records.append(record)
        self._write_json(self.records_file, records)

        # Update session query_count and updated_at
        sessions = self._read_json(self.sessions_file)
        for s in sessions:
            if s["session_id"] == session_id:
                s["query_count"] = s.get("query_count", 0) + 1
                s["updated_at"] = now
                # Auto-rename on first query
                if s["query_count"] == 1:
                    s["title"] = query[:20] + "..."
                break
        self._write_json(self.sessions_file, sessions)
        return record

    def get_records_by_session(self, session_id):
        records = self._read_json(self.records_file)
        filtered = [r for r in records if r["session_id"] == session_id]
        filtered.sort(key=lambda r: r["timestamp"])
        return filtered

    def delete_records_by_session(self, session_id):
        records = self._read_json(self.records_file)
        remaining = [r for r in records if r["session_id"] != session_id]
        deleted_count = len(records) - len(remaining)
        self._write_json(self.records_file, remaining)
        return deleted_count
