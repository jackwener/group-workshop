import json
import os
from datetime import datetime, timezone
from typing import Optional


class Storage:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, 'sessions.json')
        self.qa_records_file = os.path.join(data_dir, 'qa_records.json')
        self.reports_file = os.path.join(data_dir, 'reports.json')
        # 确保文件存在
        for f in [self.sessions_file, self.qa_records_file, self.reports_file]:
            if not os.path.exists(f):
                self._write(f, [])

    # ── 基础读写 ──────────────────────────────────────────

    def _read(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _now_iso():
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # ── 会话管理 ──────────────────────────────────────────

    def create_session(self, session_id: str, title: str = "新会话") -> dict:
        now = self._now_iso()
        session = {
            "session_id": session_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "query_count": 0,
        }
        sessions = self._read(self.sessions_file)
        sessions.append(session)
        self._write(self.sessions_file, sessions)
        return session

    def get_sessions(self) -> list:
        sessions = self._read(self.sessions_file)
        sessions.sort(key=lambda s: s["created_at"], reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> None:
        # 删除会话
        sessions = self._read(self.sessions_file)
        sessions = [s for s in sessions if s["session_id"] != session_id]
        self._write(self.sessions_file, sessions)
        # 级联删除问答记录
        records = self._read(self.qa_records_file)
        records = [r for r in records if r["session_id"] != session_id]
        self._write(self.qa_records_file, records)

    def update_session(self, session_id: str, title: str) -> Optional[dict]:
        sessions = self._read(self.sessions_file)
        for s in sessions:
            if s["session_id"] == session_id:
                s["title"] = title
                s["updated_at"] = self._now_iso()
                self._write(self.sessions_file, sessions)
                return s
        return None

    # ── 问答记录 ──────────────────────────────────────────

    def add_record(
        self,
        session_id,
        query,
        answer,
        llm_used,
        model,
        response_time_ms,
        answer_source,
        citations=None,
    ) -> dict:
        now = self._now_iso()
        ts = int(datetime.now(timezone.utc).timestamp())
        record = {
            "id": f"rec_{ts}",
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_used": llm_used,
            "model": model,
            "response_time_ms": response_time_ms,
            "answer_source": answer_source,
            "citations": citations if citations is not None else [],
            "timestamp": now,
        }
        records = self._read(self.qa_records_file)
        records.append(record)
        self._write(self.qa_records_file, records)

        # 更新 session 的 query_count 与 updated_at
        sessions = self._read(self.sessions_file)
        for s in sessions:
            if s["session_id"] == session_id:
                old_count = s["query_count"]
                s["query_count"] = old_count + 1
                s["updated_at"] = now
                # 首次问答自动命名
                if old_count == 0:
                    s["title"] = query[:20] + "..."
                break
        self._write(self.sessions_file, sessions)

        return record

    def get_records_by_session(self, session_id: str) -> list:
        records = self._read(self.qa_records_file)
        matched = [r for r in records if r["session_id"] == session_id]
        matched.sort(key=lambda r: r["timestamp"])
        return matched

    def delete_records_by_session(self, session_id: str) -> int:
        records = self._read(self.qa_records_file)
        remaining = [r for r in records if r["session_id"] != session_id]
        deleted = len(records) - len(remaining)
        self._write(self.qa_records_file, remaining)
        return deleted

    # ── 研报管理 ──────────────────────────────────────────

    def create_report(
        self, report_id, title, file_type, file_size, file_path=""
    ) -> dict:
        report = {
            "report_id": report_id,
            "title": title,
            "file_type": file_type,
            "file_size": file_size,
            "file_path": file_path,
            "status": "pending",
            "uploaded_at": self._now_iso(),
            "is_marked": False,
            "mark_status": "none",
            "parsed_result": None,
        }
        reports = self._read(self.reports_file)
        reports.append(report)
        self._write(self.reports_file, reports)
        return report

    def get_reports(self, keyword=None, rating=None, page=1, size=10) -> dict:
        reports = self._read(self.reports_file)

        # keyword 模糊匹配 title
        if keyword:
            kw = keyword.lower()
            reports = [r for r in reports if kw in r["title"].lower()]

        # rating 精确匹配（联查 parsed_result）
        if rating is not None:
            reports = [
                r
                for r in reports
                if r.get("parsed_result") is not None
                and r["parsed_result"].get("rating") == rating
            ]

        total = len(reports)
        start = (page - 1) * size
        end = start + size
        return {
            "items": reports[start:end],
            "page": page,
            "size": size,
            "total": total,
        }

    def get_report_by_id(self, report_id: str) -> Optional[dict]:
        reports = self._read(self.reports_file)
        for r in reports:
            if r["report_id"] == report_id:
                return r
        return None

    def delete_report(self, report_id: str) -> None:
        reports = self._read(self.reports_file)
        reports = [r for r in reports if r["report_id"] != report_id]
        self._write(self.reports_file, reports)

    def update_report_status(self, report_id: str, status: str) -> Optional[dict]:
        reports = self._read(self.reports_file)
        for r in reports:
            if r["report_id"] == report_id:
                r["status"] = status
                self._write(self.reports_file, reports)
                return r
        return None

    def mark_report(
        self, report_id: str, is_marked: bool, mark_status: str = "important"
    ) -> Optional[dict]:
        reports = self._read(self.reports_file)
        for r in reports:
            if r["report_id"] == report_id:
                r["is_marked"] = is_marked
                r["mark_status"] = mark_status if is_marked else "none"
                self._write(self.reports_file, reports)
                return r
        return None

    # ── 解析结果 ──────────────────────────────────────────

    def save_parse_result(self, report_id: str, parsed_result: dict) -> dict:
        reports = self._read(self.reports_file)
        for r in reports:
            if r["report_id"] == report_id:
                r["parsed_result"] = parsed_result
                self._write(self.reports_file, reports)
                return parsed_result
        return parsed_result

    def get_parse_result(self, report_id: str) -> Optional[dict]:
        reports = self._read(self.reports_file)
        for r in reports:
            if r["report_id"] == report_id:
                return r.get("parsed_result")
        return None

    def compare_reports(
        self, report_ids: list, compare_fields: list = None
    ) -> dict:
        if compare_fields is None:
            compare_fields = ["title", "rating", "target_price", "core_views"]

        rows = []
        reports = self._read(self.reports_file)
        for r in reports:
            if r["report_id"] in report_ids and r.get("parsed_result") is not None:
                pr = r["parsed_result"]
                row = {"report_id": r["report_id"]}
                for field in compare_fields:
                    row[field] = pr.get(field)
                rows.append(row)

        return {
            "headers": compare_fields,
            "rows": rows,
        }
