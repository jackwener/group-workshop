"""Storage layer - JSON file based storage for sessions, QA records and reports."""

import json
import os
import time
from datetime import datetime, timezone


class Storage:
    """JSON file storage engine. RMW (Read-Modify-Write) pattern."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.sessions_file = os.path.join(self.data_dir, "sessions.json")
        self.records_file = os.path.join(self.data_dir, "qa_records.json")
        self.reports_file = os.path.join(self.data_dir, "reports.json")

        for filepath in [self.sessions_file, self.records_file, self.reports_file]:
            if not os.path.exists(filepath):
                self._write_json(filepath, [])

    # ── internal helpers ──

    def _read_json(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _now_iso():
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # ── Session CRUD ──

    def create_session(self, session_id, title="新会话"):
        """T-002: Create a new session."""
        now = self._now_iso()
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
        """T-003: Get all sessions sorted by updated_at descending."""
        sessions = self._read_json(self.sessions_file)
        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        return sessions

    def delete_session(self, session_id):
        """T-004: Delete session + cascade delete QA records."""
        sessions = self._read_json(self.sessions_file)
        sessions = [s for s in sessions if s["session_id"] != session_id]
        self._write_json(self.sessions_file, sessions)
        self.delete_records_by_session(session_id)

    def update_session(self, session_id, **kwargs):
        """T-005: Update session fields."""
        sessions = self._read_json(self.sessions_file)
        for session in sessions:
            if session["session_id"] == session_id:
                for key, value in kwargs.items():
                    session[key] = value
                session["updated_at"] = self._now_iso()
                self._write_json(self.sessions_file, sessions)
                return session
        return None

    def get_session_by_id(self, session_id):
        """Helper: get a single session by ID."""
        sessions = self._read_json(self.sessions_file)
        for session in sessions:
            if session["session_id"] == session_id:
                return session
        return None

    def delete_records_by_session(self, session_id):
        """T-006: Delete all records for a session, return count deleted."""
        records = self._read_json(self.records_file)
        original_count = len(records)
        records = [r for r in records if r["session_id"] != session_id]
        self._write_json(self.records_file, records)
        return original_count - len(records)

    # ── QARecord CRUD ──

    def add_record(self, session_id, query, answer, llm_used, model, response_time_ms, answer_source):
        """T-022: Add a QA record. Auto-increment query_count and auto-name on first query."""
        record_id = f"rec_{int(time.time() * 1000)}"
        now = self._now_iso()
        record = {
            "id": record_id,
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
        session = self.get_session_by_id(session_id)
        if session:
            new_count = session["query_count"] + 1
            update_kwargs = {"query_count": new_count}
            # Auto-name on first query
            if new_count == 1:
                update_kwargs["title"] = query[:20] + ("..." if len(query) > 20 else "")
            self.update_session(session_id, **update_kwargs)

        return record

    def get_records_by_session(self, session_id):
        """T-023: Get all records for a session."""
        records = self._read_json(self.records_file)
        return [r for r in records if r["session_id"] == session_id]

    # ── Report CRUD ──

    def create_report(self, report_id, session_id, file_data):
        """T-042: Create a report record."""
        now = self._now_iso()
        report = {
            "report_id": report_id,
            "session_id": session_id,
            "title": file_data.get("title", ""),
            "rating": file_data.get("rating", ""),
            "target_price": file_data.get("target_price", ""),
            "core_views": file_data.get("core_views", []),
            "full_content": file_data.get("full_content", ""),
            "parsed_at": now,
            "status": "parsing",
            "file_path": file_data.get("file_path", ""),
        }
        reports = self._read_json(self.reports_file)
        reports.append(report)
        self._write_json(self.reports_file, reports)
        return report

    def get_reports(self, keyword=None, page=1, page_size=20):
        """T-043: Get reports list with optional keyword search and pagination."""
        reports = self._read_json(self.reports_file)

        if keyword:
            keyword_lower = keyword.lower()
            filtered = []
            for r in reports:
                searchable = " ".join([
                    r.get("title", ""),
                    r.get("rating", ""),
                    r.get("target_price", ""),
                    " ".join(r.get("core_views", [])),
                ])
                if keyword_lower in searchable.lower():
                    filtered.append(r)
            reports = filtered

        total = len(reports)
        page_size = min(page_size, 100)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "reports": reports[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_report_by_id(self, report_id):
        """T-044: Get single report by ID."""
        reports = self._read_json(self.reports_file)
        for report in reports:
            if report["report_id"] == report_id:
                return report
        return None

    def update_report(self, report_id, **kwargs):
        """Update report fields."""
        reports = self._read_json(self.reports_file)
        for report in reports:
            if report["report_id"] == report_id:
                for key, value in kwargs.items():
                    report[key] = value
                self._write_json(self.reports_file, reports)
                return report
        return None

    def delete_report(self, report_id):
        """T-045: Delete a report, return success."""
        reports = self._read_json(self.reports_file)
        new_reports = [r for r in reports if r["report_id"] != report_id]
        if len(new_reports) == len(reports):
            return False
        self._write_json(self.reports_file, new_reports)
        return True
