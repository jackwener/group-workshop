"""
Storage 层 - JSON 文件存储实现
对齐 10-数据模型与存储规格
"""
import json
import os
import uuid
import fcntl
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from pathlib import Path


class Storage:
    """JSON 文件存储类"""
    
    def __init__(self, data_dir: str = None):
        """初始化存储
        
        Args:
            data_dir: 数据目录路径，默认从环境变量获取
        """
        self.data_dir = Path(data_dir or os.getenv('DATA_DIR', './data'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.sessions_file = self.data_dir / 'sessions.json'
        self.qa_records_file = self.data_dir / 'qa_records.json'
        
        # 初始化空文件
        self._init_file(self.sessions_file, [])
        self._init_file(self.qa_records_file, [])
    
    def _init_file(self, file_path: Path, default_data: Any):
        """初始化文件，如果不存在则创建"""
        if not file_path.exists():
            self._write_file(file_path, default_data)
    
    def _read_file(self, file_path: Path) -> Any:
        """读取 JSON 文件（带文件锁）"""
        with open(file_path, 'r', encoding='utf-8') as f:
            # 获取共享锁（读锁）
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def _write_file(self, file_path: Path, data: Any):
        """写入 JSON 文件（带文件锁）"""
        with open(file_path, 'w', encoding='utf-8') as f:
            # 获取独占锁（写锁）
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    # ==================== Session 操作方法 ====================
    
    def create_session(self, title: str = "新会话") -> Dict[str, Any]:
        """创建新会话
        
        Args:
            title: 会话标题，默认"新会话"
            
        Returns:
            创建的会话对象
        """
        sessions = self._read_file(self.sessions_file)
        
        now = datetime.now(timezone.utc).isoformat()
        session = {
            "session_id": str(uuid.uuid4()),
            "title": title[:23] if title else "新会话",  # 最大23字符
            "created_at": now,
            "updated_at": now,
            "query_count": 0,
            "deleted": False
        }
        
        sessions.append(session)
        self._write_file(self.sessions_file, sessions)
        
        return session
    
    def get_sessions(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """获取所有会话列表
        
        Args:
            include_deleted: 是否包含已删除的会话
            
        Returns:
            会话列表，按更新时间倒序排列
        """
        sessions = self._read_file(self.sessions_file)
        
        # 过滤已删除的会话
        if not include_deleted:
            sessions = [s for s in sessions if not s.get("deleted", False)]
        
        # 按更新时间倒序排列
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return sessions
    
    def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话对象，如果不存在返回 None
        """
        sessions = self._read_file(self.sessions_file)
        
        for session in sessions:
            if session["session_id"] == session_id and not session.get("deleted", False):
                return session
        
        return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新会话
        
        Args:
            session_id: 会话 ID
            updates: 更新的字段
            
        Returns:
            更新后的会话对象，如果不存在返回 None
        """
        sessions = self._read_file(self.sessions_file)
        
        for session in sessions:
            if session["session_id"] == session_id and not session.get("deleted", False):
                session.update(updates)
                session["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._write_file(self.sessions_file, sessions)
                return session
        
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话（软删除 + 级联删除记录）
        
        Args:
            session_id: 会话 ID
            
        Returns:
            是否删除成功
        """
        sessions = self._read_file(self.sessions_file)
        
        for session in sessions:
            if session["session_id"] == session_id and not session.get("deleted", False):
                # 软删除
                session["deleted"] = True
                session["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._write_file(self.sessions_file, sessions)
                
                # 级联删除关联的 QARecord
                self.delete_records_by_session(session_id)
                
                return True
        
        return False
    
    def increment_query_count(self, session_id: str) -> Optional[int]:
        """增加会话的 query_count
        
        Args:
            session_id: 会话 ID
            
        Returns:
            更新后的 query_count，如果不存在返回 None
        """
        session = self.get_session_by_id(session_id)
        if session:
            new_count = session.get("query_count", 0) + 1
            self.update_session(session_id, {"query_count": new_count})
            
            # 首次问答自动命名（query_count 从 0 -> 1）
            if session.get("query_count", 0) == 0:
                return new_count
            return new_count
        return None
    
    def auto_rename_session(self, session_id: str, query: str):
        """首次问答自动命名
        
        Args:
            session_id: 会话 ID
            query: 用户提问内容
        """
        session = self.get_session_by_id(session_id)
        if session and session.get("query_count", 0) == 1 and session.get("title") == "新会话":
            # 取 query 前 20 字 + ...
            new_title = query[:20] + ("..." if len(query) > 20 else "")
            self.update_session(session_id, {"title": new_title})
    
    # ==================== QARecord 操作方法 ====================
    
    def add_record(self, session_id: str, query: str, answer: str,
                   llm_used: bool, model: Optional[str], 
                   answer_source: Optional[str],
                   response_time_ms: int) -> Dict[str, Any]:
        """添加问答记录
        
        Args:
            session_id: 会话 ID
            query: 用户提问
            answer: AI 回答
            llm_used: 是否使用真实 LLM
            model: 模型标识
            answer_source: 回答来源 (copaw/bailian/demo)
            response_time_ms: 响应耗时（毫秒）
            
        Returns:
            创建的记录对象
        """
        records = self._read_file(self.qa_records_file)
        
        now = datetime.now(timezone.utc)
        record = {
            "id": f"rec_{int(now.timestamp())}",
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_used": llm_used,
            "model": model,
            "answer_source": answer_source,
            "response_time_ms": response_time_ms,
            "timestamp": now.isoformat()
        }
        
        records.append(record)
        self._write_file(self.qa_records_file, records)
        
        # 更新会话的 query_count 和 updated_at
        self.increment_query_count(session_id)
        
        # 首次问答自动命名
        self.auto_rename_session(session_id, query)
        
        return record
    
    def get_records_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """获取指定会话的所有记录
        
        Args:
            session_id: 会话 ID
            
        Returns:
            记录列表，按时间正序排列
        """
        records = self._read_file(self.qa_records_file)
        
        # 过滤并排序
        session_records = [r for r in records if r["session_id"] == session_id]
        session_records.sort(key=lambda x: x.get("timestamp", ""))
        
        return session_records
    
    def delete_records_by_session(self, session_id: str) -> int:
        """删除指定会话的所有记录（级联删除）
        
        Args:
            session_id: 会话 ID
            
        Returns:
            删除的记录数量
        """
        records = self._read_file(self.qa_records_file)
        
        original_count = len(records)
        records = [r for r in records if r["session_id"] != session_id]
        deleted_count = original_count - len(records)
        
        self._write_file(self.qa_records_file, records)
        
        return deleted_count


# 全局存储实例
_storage_instance: Optional[Storage] = None


def get_storage() -> Storage:
    """获取全局存储实例（单例模式）"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = Storage()
    return _storage_instance
