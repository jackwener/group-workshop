"""
Storage 层 - JSON 文件存储实现
对齐 10-数据模型与存储规格.md
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any


class Storage:
    """JSON 文件存储实现"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        self.records_file = os.path.join(data_dir, "qa_records.json")
        self.files_file = os.path.join(data_dir, "report_files.json")
        
        # 确保目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化空文件
        self._init_file(self.sessions_file, [])
        self._init_file(self.records_file, [])
        self._init_file(self.files_file, [])
    
    def _init_file(self, filepath: str, default_data: Any):
        """初始化文件，如果不存在则创建"""
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    def _read_json(self, filepath: str) -> Any:
        """读取 JSON 文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_json(self, filepath: str, data: Any):
        """写入 JSON 文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _now_iso(self) -> str:
        """获取当前 ISO-8601 格式时间"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _generate_id(self) -> str:
        """生成 UUID"""
        return str(uuid.uuid4())
    
    # ==================== 会话管理 ====================
    
    def create_session(self, title: str = "新会话") -> Dict:
        """创建新会话"""
        sessions = self._read_json(self.sessions_file)
        
        session = {
            "session_id": self._generate_id(),
            "title": title,
            "created_at": self._now_iso(),
            "updated_at": self._now_iso(),
            "query_count": 0,
            "status": "active"
        }
        
        sessions.append(session)
        self._write_json(self.sessions_file, sessions)
        
        return session
    
    def get_sessions(self) -> List[Dict]:
        """获取全部会话列表，按 updated_at 倒序"""
        sessions = self._read_json(self.sessions_file)
        # 过滤已删除的会话
        sessions = [s for s in sessions if s.get("status") != "deleted"]
        # 按 updated_at 倒序
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取单个会话详情"""
        sessions = self._read_json(self.sessions_file)
        for session in sessions:
            if session.get("session_id") == session_id and session.get("status") != "deleted":
                return session
        return None
    
    def update_session(self, session_id: str, data: Dict) -> Optional[Dict]:
        """更新会话信息"""
        sessions = self._read_json(self.sessions_file)
        
        for session in sessions:
            if session.get("session_id") == session_id:
                # 允许更新的字段
                if "title" in data:
                    session["title"] = data["title"]
                if "status" in data:
                    session["status"] = data["status"]
                if "query_count" in data:
                    session["query_count"] = data["query_count"]
                
                session["updated_at"] = self._now_iso()
                self._write_json(self.sessions_file, sessions)
                return session
        
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话（软删除）+ 级联删除关联记录"""
        # 软删除会话
        sessions = self._read_json(self.sessions_file)
        session_found = False
        
        for session in sessions:
            if session.get("session_id") == session_id:
                session["status"] = "deleted"
                session["updated_at"] = self._now_iso()
                session_found = True
                break
        
        if not session_found:
            return False
        
        self._write_json(self.sessions_file, sessions)
        
        # 级联删除问答记录
        self.delete_records_by_session(session_id)
        
        # 级联删除文件记录
        files = self._read_json(self.files_file)
        files = [f for f in files if f.get("session_id") != session_id]
        self._write_json(self.files_file, files)
        
        return True
    
    # ==================== 问答记录管理 ====================
    
    def add_record(self, session_id: str, query: str, answer: str,
                   llm_used: bool, model: Optional[str],
                   response_time_ms: int, answer_source: Optional[str],
                   file_id: Optional[str] = None) -> Optional[Dict]:
        """写入问答记录"""
        # 检查会话是否存在
        session = self.get_session(session_id)
        if not session:
            return None
        
        records = self._read_json(self.records_file)
        
        record = {
            "id": f"rec_{int(datetime.now().timestamp() * 1000)}",
            "session_id": session_id,
            "file_id": file_id,
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
        
        # 更新会话的 query_count 和 updated_at
        self.update_session(session_id, {
            "query_count": session.get("query_count", 0) + 1
        })
        
        return record
    
    def get_records_by_session(self, session_id: str) -> List[Dict]:
        """按 session_id 过滤，按 timestamp 倒序返回"""
        records = self._read_json(self.records_file)
        records = [r for r in records if r.get("session_id") == session_id]
        # 按 timestamp 升序排列，最新的在后面
        records.sort(key=lambda x: x.get("timestamp", ""))
        return records
    
    def get_record(self, record_id: str) -> Optional[Dict]:
        """获取单条记录详情"""
        records = self._read_json(self.records_file)
        for record in records:
            if record.get("id") == record_id:
                return record
        return None
    
    def delete_records_by_session(self, session_id: str) -> int:
        """删除指定会话下所有问答记录，返回删除数量"""
        records = self._read_json(self.records_file)
        original_count = len(records)
        records = [r for r in records if r.get("session_id") != session_id]
        deleted_count = original_count - len(records)
        self._write_json(self.records_file, records)
        return deleted_count
    
    # ==================== 研报文件管理 ====================
    
    def save_file(self, session_id: str, file_name: str, file_size: int,
                  file_type: str, file_path: str) -> Optional[Dict]:
        """保存文件元数据"""
        # 检查会话是否存在
        session = self.get_session(session_id)
        if not session:
            return None
        
        files = self._read_json(self.files_file)
        
        file_info = {
            "file_id": self._generate_id(),
            "session_id": session_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
            "file_path": file_path,
            "parse_status": "pending",
            "parse_progress": None,
            "parse_result": None,
            "created_at": self._now_iso(),
            "updated_at": self._now_iso()
        }
        
        files.append(file_info)
        self._write_json(self.files_file, files)
        
        return file_info
    
    def get_files_by_session(self, session_id: str) -> List[Dict]:
        """获取会话下所有文件，按 created_at 倒序"""
        files = self._read_json(self.files_file)
        files = [f for f in files if f.get("session_id") == session_id]
        files.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return files
    
    def get_file(self, file_id: str) -> Optional[Dict]:
        """获取单个文件详情"""
        files = self._read_json(self.files_file)
        for file_info in files:
            if file_info.get("file_id") == file_id:
                return file_info
        return None
    
    def update_parse_status(self, file_id: str, parse_status: str,
                           parse_progress: Optional[int] = None,
                           parse_result: Optional[Dict] = None) -> Optional[Dict]:
        """更新解析状态、进度和结果"""
        files = self._read_json(self.files_file)
        
        for file_info in files:
            if file_info.get("file_id") == file_id:
                file_info["parse_status"] = parse_status
                if parse_progress is not None:
                    file_info["parse_progress"] = parse_progress
                if parse_result is not None:
                    file_info["parse_result"] = parse_result
                file_info["updated_at"] = self._now_iso()
                
                self._write_json(self.files_file, files)
                return file_info
        
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """删除文件记录"""
        files = self._read_json(self.files_file)
        original_count = len(files)
        files = [f for f in files if f.get("file_id") != file_id]
        
        if len(files) == original_count:
            return False
        
        self._write_json(self.files_file, files)
        return True
