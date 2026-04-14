"""
Storage 层 — 对齐 Spec 10 数据模型与存储规格
JSON 文件存储：sessions.json + qa_records.json
"""
import json
import os
import time
import uuid
from datetime import datetime, timezone


class Storage:
    """JSON 文件存储引擎，RMW 模式（全量读入 → 修改 → 全量写回）"""

    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.records_file = os.path.join(data_dir, "qa_records.json")

        # 目录不存在时自动创建 (TC-M01-040)
        os.makedirs(data_dir, exist_ok=True)

        # 初始化空 JSON 文件
        if not os.path.exists(self.sessions_file):
            self._write_json(self.sessions_file, [])
        if not os.path.exists(self.records_file):
            self._write_json(self.records_file, [])

    # ── 内部工具 ──

    def _read_json(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _now_iso(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ── 5.1 会话管理 ──

    def create_session(self, session_id=None, title="新会话"):
        """创建新会话 (TC-M01-041)"""
        sessions = self._read_json(self.sessions_file)
        now = self._now_iso()
        session = {
            "session_id": session_id or str(uuid.uuid4()),
            "title": title[:23] if title else "新会话",
            "created_at": now,
            "updated_at": now,
            "query_count": 0,
        }
        sessions.append(session)
        self._write_json(self.sessions_file, sessions)
        return session

    def get_sessions(self):
        """返回全部会话列表，按 updated_at 倒序 (TC-M01-042)"""
        sessions = self._read_json(self.sessions_file)
        sessions.sort(key=lambda s: s["updated_at"], reverse=True)
        return sessions

    def delete_session(self, session_id):
        """删除会话 + 级联删除关联记录 (TC-M01-043)"""
        sessions = self._read_json(self.sessions_file)
        new_sessions = [s for s in sessions if s["session_id"] != session_id]
        if len(new_sessions) == len(sessions):
            return None  # 未找到
        self._write_json(self.sessions_file, new_sessions)
        deleted_count = self.delete_records_by_session(session_id)
        return deleted_count

    def update_session(self, session_id, title=None, query_count=None):
        """更新会话标题和问答计数 (TC-M01-046)"""
        sessions = self._read_json(self.sessions_file)
        for session in sessions:
            if session["session_id"] == session_id:
                if title is not None:
                    session["title"] = title[:23]
                if query_count is not None:
                    session["query_count"] = query_count
                session["updated_at"] = self._now_iso()
                self._write_json(self.sessions_file, sessions)
                return session
        return None

    def get_session(self, session_id):
        """获取单个会话"""
        sessions = self._read_json(self.sessions_file)
        for session in sessions:
            if session["session_id"] == session_id:
                return session
        return None

    # ── 5.2 问答记录管理 ──

    def add_record(self, session_id, query, answer, llm_used=False,
                   model=None, response_time_ms=0, answer_source="demo"):
        """写入记录 + 更新 query_count + 首次自动命名 (TC-M01-044)"""
        records = self._read_json(self.records_file)
        record = {
            "id": f"rec_{int(time.time() * 1000)}",
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_used": llm_used,
            "model": model,
            "response_time_ms": response_time_ms,
            "answer_source": answer_source,
            "timestamp": self._now_iso(),
        }
        records.append(record)
        self._write_json(self.records_file, records)

        # 更新会话的 query_count 和 updated_at
        session = self.get_session(session_id)
        if session:
            new_count = session["query_count"] + 1
            # 首次问答自动命名（Spec 10 §6）
            new_title = session["title"]
            if new_count == 1:
                new_title = query[:20] + ("..." if len(query) > 20 else "")
            self.update_session(session_id, title=new_title, query_count=new_count)

        return record

    def get_records_by_session(self, session_id):
        """按 session_id 过滤记录，按 timestamp 正序 (TC-M01-045)"""
        records = self._read_json(self.records_file)
        filtered = [r for r in records if r["session_id"] == session_id]
        filtered.sort(key=lambda r: r["timestamp"])
        return filtered

    def delete_records_by_session(self, session_id):
        """删除指定会话的所有记录，返回删除数量 (TC-M01-047)"""
        records = self._read_json(self.records_file)
        new_records = [r for r in records if r["session_id"] != session_id]
        deleted_count = len(records) - len(new_records)
        self._write_json(self.records_file, new_records)
        return deleted_count
