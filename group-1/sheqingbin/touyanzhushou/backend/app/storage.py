"""
投研问答助手 - 数据存储层
使用 JSON 文件存储，支持 Session 和 QARecord 的 CRUD 操作
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


class Storage:
    """
    JSON 文件存储实现
    文件布局: {data_dir}/sessions.json + qa_records.json
    """
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.records_file = os.path.join(data_dir, "qa_records.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化文件
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
            return []
    
    def _write_json(self, filepath: str, data: Any):
        """写入 JSON 文件（带缩进）"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _now_iso(self) -> str:
        """获取当前 UTC 时间的 ISO-8601 格式"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # ==================== Session 管理 ====================
    
    def create_session(self, title: Optional[str] = None) -> Dict[str, Any]:
        """
        创建新会话
        
        Args:
            title: 会话标题，默认"新会话"
            
        Returns:
            创建的会话对象
        """
        sessions = self._read_json(self.sessions_file)
        
        now = self._now_iso()
        session = {
            "session_id": str(uuid.uuid4()),
            "title": title[:23] if title and len(title) > 23 else (title or "新会话"),
            "created_at": now,
            "updated_at": now,
            "query_count": 0
        }
        
        sessions.append(session)
        self._write_json(self.sessions_file, sessions)
        
        return session
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """
        获取所有会话列表
        
        Returns:
            会话列表（按更新时间倒序）
        """
        sessions = self._read_json(self.sessions_file)
        # 按 updated_at 倒序排列
        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话对象，不存在返回 None
        """
        sessions = self._read_json(self.sessions_file)
        for session in sessions:
            if session["session_id"] == session_id:
                return session
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话（级联删除关联记录）
        
        Args:
            session_id: 会话 ID
            
        Returns:
            是否删除成功
        """
        sessions = self._read_json(self.sessions_file)
        original_len = len(sessions)
        
        # 过滤掉目标会话
        sessions = [s for s in sessions if s["session_id"] != session_id]
        
        if len(sessions) == original_len:
            return False
        
        self._write_json(self.sessions_file, sessions)
        
        # 级联删除关联记录
        self.delete_records_by_session(session_id)
        
        return True
    
    def update_session(self, session_id: str, title: Optional[str] = None, 
                       updated_at: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        更新会话信息
        
        Args:
            session_id: 会话 ID
            title: 新标题
            updated_at: 更新时间
            
        Returns:
            更新后的会话对象，不存在返回 None
        """
        sessions = self._read_json(self.sessions_file)
        
        for session in sessions:
            if session["session_id"] == session_id:
                if title is not None:
                    session["title"] = title[:23] if len(title) > 23 else title
                if updated_at is not None:
                    session["updated_at"] = updated_at
                
                self._write_json(self.sessions_file, sessions)
                return session
        
        return None
    
    def increment_query_count(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        增加会话的问答计数
        
        Args:
            session_id: 会话 ID
            
        Returns:
            更新后的会话对象
        """
        sessions = self._read_json(self.sessions_file)
        
        for session in sessions:
            if session["session_id"] == session_id:
                session["query_count"] = session.get("query_count", 0) + 1
                session["updated_at"] = self._now_iso()
                self._write_json(self.sessions_file, sessions)
                return session
        
        return None
    
    # ==================== QARecord 管理 ====================
    
    def add_record(self, session_id: str, query: str, answer: str,
                   llm_used: bool, model: Optional[str], 
                   response_time_ms: int, answer_source: str) -> Dict[str, Any]:
        """
        添加问答记录
        
        Args:
            session_id: 所属会话 ID
            query: 用户提问
            answer: AI 回答
            llm_used: 是否使用真实 LLM
            model: 模型标识
            response_time_ms: 响应耗时
            answer_source: 回答来源 (copaw/bailian/demo)
            
        Returns:
            创建的记录对象
        """
        records = self._read_json(self.records_file)
        
        # 生成记录 ID: rec_{timestamp_ms}
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        record_id = f"rec_{timestamp_ms}"
        
        record = {
            "id": record_id,
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
        
        # 更新会话计数
        self.increment_query_count(session_id)
        
        # 首次问答自动命名
        session = self.get_session(session_id)
        if session and session.get("query_count") == 1:
            auto_title = query[:20] + ("..." if len(query) > 20 else "")
            self.update_session(session_id, title=auto_title)
        
        return record
    
    def get_records_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取指定会话的所有问答记录
        
        Args:
            session_id: 会话 ID
            
        Returns:
            问答记录列表（按时间正序）
        """
        records = self._read_json(self.records_file)
        session_records = [r for r in records if r["session_id"] == session_id]
        # 按时间正序排列
        return sorted(session_records, key=lambda x: x.get("timestamp", ""))
    
    def delete_records_by_session(self, session_id: str) -> int:
        """
        删除指定会话的所有记录
        
        Args:
            session_id: 会话 ID
            
        Returns:
            删除的记录数量
        """
        records = self._read_json(self.records_file)
        original_len = len(records)
        
        records = [r for r in records if r["session_id"] != session_id]
        deleted_count = original_len - len(records)
        
        self._write_json(self.records_file, records)
        return deleted_count


# 全局存储实例（单例模式）
_storage_instance: Optional[Storage] = None


def get_storage(data_dir: str = "./data") -> Storage:
    """获取存储实例（单例）"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = Storage(data_dir)
    return _storage_instance
