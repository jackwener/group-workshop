"""
Storage 层 - JSON 文件存储
对齐 10-数据模型与存储规格 §5 Storage 方法清单
职责：仅限文件 CRUD 操作（禁止调用外部 API）
"""
import json
import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any


class Storage:
    """
    JSON 文件存储管理类
    存储引擎：JSON 文件（UTF-8，缩进 2 空格）
    文件布局：{DATA_DIR}/sessions.json + qa_records.json
    """
    
    def __init__(self, data_dir: str = None):
        """初始化存储，确保数据目录和文件存在"""
        self.data_dir = data_dir or os.getenv("DATA_DIR", "./data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.sessions_file = os.path.join(self.data_dir, "sessions.json")
        self.records_file = os.path.join(self.data_dir, "qa_records.json")
        
        # 初始化空文件
        self._init_file(self.sessions_file, [])
        self._init_file(self.records_file, [])
    
    def _init_file(self, filepath: str, default_data: Any):
        """初始化 JSON 文件（如果不存在）"""
        if not os.path.exists(filepath):
            self._write_json(filepath, default_data)
    
    def _read_json(self, filepath: str) -> Any:
        """读取 JSON 文件"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return [] if filepath.endswith(".json") else {}
    
    def _write_json(self, filepath: str, data: Any):
        """写入 JSON 文件（缩进 2 空格）"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _now_iso(self) -> str:
        """返回当前 UTC 时间 ISO-8601 格式"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # ==================== 会话管理 ====================
    
    def create_session(self, session_id: str, title: str = "新会话") -> Dict:
        """
        创建新会话
        对齐 TC-M01-001, TC-M01-002
        """
        sessions = self._read_json(self.sessions_file)
        
        now = self._now_iso()
        session = {
            "session_id": session_id,
            "title": title[:23],  # 约束：≤23 字符
            "created_at": now,
            "updated_at": now,
            "query_count": 0
        }
        sessions.append(session)
        self._write_json(self.sessions_file, sessions)
        return session
    
    def get_sessions(self) -> List[Dict]:
        """
        返回全部会话，按 created_at 倒序排列
        对齐 TC-M01-003
        """
        sessions = self._read_json(self.sessions_file)
        return sorted(sessions, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """根据 ID 获取单个会话"""
        sessions = self._read_json(self.sessions_file)
        for s in sessions:
            if s.get("session_id") == session_id:
                return s
        return None
    
    def delete_session(self, session_id: str) -> int:
        """
        删除会话 + 级联删除关联记录
        返回删除的记录数
        对齐 TC-M01-004, TC-M01-005
        """
        # 删除会话
        sessions = self._read_json(self.sessions_file)
        original_count = len(sessions)
        sessions = [s for s in sessions if s.get("session_id") != session_id]
        self._write_json(self.sessions_file, sessions)
        
        # 级联删除关联记录
        deleted_records = self.delete_records_by_session(session_id)
        
        return deleted_records
    
    def update_session(self, session_id: str, updates: Dict) -> Optional[Dict]:
        """
        更新会话字段
        对齐 TC-M01-006
        """
        sessions = self._read_json(self.sessions_file)
        for i, s in enumerate(sessions):
            if s.get("session_id") == session_id:
                sessions[i].update(updates)
                sessions[i]["updated_at"] = self._now_iso()
                self._write_json(self.sessions_file, sessions)
                return sessions[i]
        return None
    
    # ==================== 问答记录管理 ====================
    
    def add_record(self, session_id: str, query: str, answer: str,
                   llm_used: bool, model: Optional[str],
                   response_time_ms: int, answer_source: str) -> Dict:
        """
        写入记录 + 更新 session.query_count 和 updated_at
        对齐 TC-M01-007, TC-M01-010（首次问答自动命名）
        """
        records = self._read_json(self.records_file)
        
        # 生成 record_id: rec_{timestamp}
        record_id = f"rec_{int(time.time() * 1000)}"
        
        record = {
            "record_id": record_id,
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_used": llm_used,
            "model": model,
            "response_time_ms": response_time_ms,
            "answer_source": answer_source,
            "timestamp": self._now_iso()
        }
        records.append(record)
        self._write_json(self.records_file, records)
        
        # 更新会话：query_count + 1，updated_at 更新
        session = self.get_session(session_id)
        if session:
            new_count = session.get("query_count", 0) + 1
            updates = {
                "query_count": new_count,
                "updated_at": self._now_iso()
            }
            
            # 首次问答自动命名（query_count 从 0 → 1）
            # 对齐 10-数据模型 §6 关键业务逻辑
            if session.get("query_count", 0) == 0:
                new_title = query[:20] + ("..." if len(query) > 20 else "")
                updates["title"] = new_title
            
            self.update_session(session_id, updates)
        
        return record
    
    def get_records_by_session(self, session_id: str) -> List[Dict]:
        """
        按 session_id 过滤，按 timestamp 正序排列
        对齐 TC-M01-008
        """
        records = self._read_json(self.records_file)
        filtered = [r for r in records if r.get("session_id") == session_id]
        return sorted(filtered, key=lambda x: x.get("timestamp", ""))
    
    def delete_records_by_session(self, session_id: str) -> int:
        """
        删除指定会话下的所有记录，返回删除数量
        对齐 TC-M01-009
        """
        records = self._read_json(self.records_file)
        original_count = len(records)
        records = [r for r in records if r.get("session_id") != session_id]
        self._write_json(self.records_file, records)
        return original_count - len(records)
