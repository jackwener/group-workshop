"""
数据存储层 - JSON文件存储实现
基于规格文档 10-数据模型与存储规格 实现
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path


class Storage:
    """JSON文件存储类，管理Session、QARecord、Report数据"""
    
    def __init__(self, data_dir: str = None):
        """初始化存储，设置数据目录和文件路径"""
        if data_dir is None:
            # 默认使用 backend/data 目录
            backend_dir = Path(__file__).parent.parent.parent
            data_dir = backend_dir / "data"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 定义数据文件路径
        self.sessions_file = self.data_dir / "sessions.json"
        self.records_file = self.data_dir / "qa_records.json"
        self.reports_file = self.data_dir / "reports.json"
        
        # 确保数据文件存在
        self._ensure_file_exists(self.sessions_file)
        self._ensure_file_exists(self.records_file)
        self._ensure_file_exists(self.reports_file)
    
    def _ensure_file_exists(self, file_path: Path):
        """确保数据文件存在，不存在则创建空列表"""
        if not file_path.exists():
            self._write_json(file_path, [])
    
    def _read_json(self, file_path: Path) -> list:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_json(self, file_path: Path, data: list):
        """写入JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _now_iso(self) -> str:
        """获取当前时间的ISO-8601 UTC格式"""
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    def _generate_record_id(self) -> str:
        """生成问答记录ID：rec_{timestamp}"""
        ts = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:-3]
        return f"rec_{ts}"
    
    # ==================== 会话管理 ====================
    
    def create_session(self, session_id: str, title: str = "新会话") -> dict:
        """
        创建新会话
        
        Args:
            session_id: 会话唯一标识(UUID)
            title: 会话标题，默认"新会话"
        
        Returns:
            创建的会话数据
        
        Raises:
            ValueError: 会话ID已存在
        """
        sessions = self._read_json(self.sessions_file)
        
        # 检查session_id是否已存在
        if any(s["session_id"] == session_id for s in sessions):
            raise ValueError(f"Session with id {session_id} already exists")
        
        now = self._now_iso()
        session = {
            "session_id": session_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "query_count": 0
        }
        
        sessions.append(session)
        self._write_json(self.sessions_file, sessions)
        
        return session
    
    def get_sessions(self, page: int = 1, page_size: int = 20) -> list:
        """
        分页获取会话列表，按updated_at倒序
        
        Args:
            page: 页码，默认1
            page_size: 每页大小，默认20，最大100
        
        Returns:
            会话列表
        """
        # 分页参数校验
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        
        sessions = self._read_json(self.sessions_file)
        
        # 按updated_at倒序排序
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        
        return sessions[start:end]
    
    def get_session_by_id(self, session_id: str) -> Optional[dict]:
        """
        根据ID获取单个会话详情
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话数据，不存在返回None
        """
        sessions = self._read_json(self.sessions_file)
        
        for session in sessions:
            if session["session_id"] == session_id:
                return session
        
        return None
    
    def update_session(self, session_id: str, title: str) -> dict:
        """
        更新会话标题
        
        Args:
            session_id: 会话ID
            title: 新标题
        
        Returns:
            更新后的会话数据
        
        Raises:
            ValueError: 会话不存在
        """
        sessions = self._read_json(self.sessions_file)
        
        for session in sessions:
            if session["session_id"] == session_id:
                session["title"] = title
                session["updated_at"] = self._now_iso()
                self._write_json(self.sessions_file, sessions)
                return session
        
        raise ValueError(f"Session with id {session_id} not found")
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话，级联删除该会话下所有问答记录
        
        Args:
            session_id: 会话ID
        
        Returns:
            是否删除成功
        """
        sessions = self._read_json(self.sessions_file)
        
        # 查找并删除会话
        original_len = len(sessions)
        sessions = [s for s in sessions if s["session_id"] != session_id]
        
        if len(sessions) == original_len:
            return False
        
        self._write_json(self.sessions_file, sessions)
        
        # 级联删除问答记录
        self.delete_records_by_session(session_id)
        
        return True
    
    # ==================== 问答记录管理 ====================
    
    def add_record(self, session_id: str, query: str, answer: str,
                   llm_used: bool, model: Optional[str],
                   response_time_ms: int, answer_source: str) -> dict:
        """
        写入问答记录，同时更新对应会话的query_count和updated_at
        
        Args:
            session_id: 所属会话ID
            query: 用户提问原文
            answer: LLM/Demo返回的答案
            llm_used: 是否使用真实LLM
            model: 模型标识
            response_time_ms: 响应耗时(ms)
            answer_source: 答案来源(copaw|bailian|demo)
        
        Returns:
            创建的问答记录
        
        Raises:
            ValueError: 会话不存在
        """
        # 验证会话存在
        sessions = self._read_json(self.sessions_file)
        session = None
        for s in sessions:
            if s["session_id"] == session_id:
                session = s
                break
        
        if session is None:
            raise ValueError(f"Session with id {session_id} not found")
        
        # 创建问答记录
        record = {
            "record_id": self._generate_record_id(),
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "llm_used": llm_used,
            "model": model,
            "response_time_ms": response_time_ms,
            "answer_source": answer_source,
            "timestamp": self._now_iso()
        }
        
        records = self._read_json(self.records_file)
        records.append(record)
        self._write_json(self.records_file, records)
        
        # 更新会话的query_count和updated_at
        session["query_count"] += 1
        session["updated_at"] = self._now_iso()
        
        # 首次问答自动命名（query_count 从 0 -> 1）
        if session["query_count"] == 1:
            new_title = query[:20] + ("..." if len(query) > 20 else "")
            session["title"] = new_title
        
        self._write_json(self.sessions_file, sessions)
        
        return record
    
    def get_records_by_session(self, session_id: str, 
                               page: int = 1, page_size: int = 20) -> list:
        """
        按session_id分页查询问答记录，按timestamp倒序
        
        Args:
            session_id: 会话ID
            page: 页码，默认1
            page_size: 每页大小，默认20，最大100
        
        Returns:
            问答记录列表
        """
        # 分页参数校验
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        
        records = self._read_json(self.records_file)
        
        # 筛选指定会话的记录
        session_records = [r for r in records if r["session_id"] == session_id]
        
        # 按timestamp倒序排序
        session_records.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        
        return session_records[start:end]
    
    def get_record_by_id(self, record_id: str) -> Optional[dict]:
        """
        根据ID获取单条记录详情
        
        Args:
            record_id: 记录ID
        
        Returns:
            记录数据，不存在返回None
        """
        records = self._read_json(self.records_file)
        
        for record in records:
            if record["record_id"] == record_id:
                return record
        
        return None
    
    def delete_records_by_session(self, session_id: str) -> int:
        """
        删除指定会话下的所有问答记录
        
        Args:
            session_id: 会话ID
        
        Returns:
            删除的记录数量
        """
        records = self._read_json(self.records_file)
        
        original_len = len(records)
        records = [r for r in records if r["session_id"] != session_id]
        
        deleted_count = original_len - len(records)
        
        if deleted_count > 0:
            self._write_json(self.records_file, records)
        
        return deleted_count
    
    # ==================== 研报管理 ====================
    
    def create_report(self, report_id: str, title: str, 
                      filename: str, file_size: int) -> dict:
        """
        创建研报记录
        
        Args:
            report_id: 研报唯一标识
            title: 研报标题
            filename: 文件名
            file_size: 文件大小(字节)
        
        Returns:
            创建的研报数据
        
        Raises:
            ValueError: 研报ID已存在
        """
        reports = self._read_json(self.reports_file)
        
        # 检查report_id是否已存在
        if any(r["report_id"] == report_id for r in reports):
            raise ValueError(f"Report with id {report_id} already exists")
        
        now = self._now_iso()
        report = {
            "report_id": report_id,
            "title": title,
            "filename": filename,
            "file_size": file_size,
            "uploaded_at": now,
            "analyzed_at": None,
            "status": "pending",
            "analysis": None
        }
        
        reports.append(report)
        self._write_json(self.reports_file, reports)
        
        return report
    
    def get_reports(self, page: int = 1, page_size: int = 20, 
                    status: Optional[str] = None) -> list:
        """
        分页查询研报列表，支持按status筛选，按uploaded_at倒序
        
        Args:
            page: 页码，默认1
            page_size: 每页大小，默认20，最大100
            status: 状态筛选(pending|analyzing|analyzed|failed)
        
        Returns:
            研报列表
        """
        # 分页参数校验
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        
        reports = self._read_json(self.reports_file)
        
        # 按status筛选
        if status:
            reports = [r for r in reports if r.get("status") == status]
        
        # 按uploaded_at倒序排序
        reports.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        
        return reports[start:end]
    
    def get_report_by_id(self, report_id: str) -> Optional[dict]:
        """
        根据ID获取单个研报详情
        
        Args:
            report_id: 研报ID
        
        Returns:
            研报数据，不存在返回None
        """
        reports = self._read_json(self.reports_file)
        
        for report in reports:
            if report["report_id"] == report_id:
                return report
        
        return None
    
    def delete_report(self, report_id: str) -> bool:
        """
        删除研报记录及关联文件
        
        Args:
            report_id: 研报ID
        
        Returns:
            是否删除成功
        """
        reports = self._read_json(self.reports_file)
        
        # 查找要删除的研报
        report_to_delete = None
        for r in reports:
            if r["report_id"] == report_id:
                report_to_delete = r
                break
        
        if report_to_delete is None:
            return False
        
        # 删除记录
        reports = [r for r in reports if r["report_id"] != report_id]
        self._write_json(self.reports_file, reports)
        
        # 删除关联的文件
        if report_to_delete.get("filename"):
            file_path = self.data_dir / "uploads" / report_to_delete["filename"]
            if file_path.exists():
                try:
                    file_path.unlink()
                except OSError:
                    pass  # 文件删除失败不影响记录删除结果
        
        return True
    
    def update_report_status(self, report_id: str, status: str,
                             analysis: Optional[dict] = None) -> dict:
        """
        更新研报分析状态和结果
        
        Args:
            report_id: 研报ID
            status: 新状态(pending|analyzing|analyzed|failed)
            analysis: 分析结果数据
        
        Returns:
            更新后的研报数据
        
        Raises:
            ValueError: 研报不存在
        """
        reports = self._read_json(self.reports_file)
        
        for report in reports:
            if report["report_id"] == report_id:
                report["status"] = status
                report["analysis"] = analysis
                
                # 当状态为analyzed时，自动更新analyzed_at
                if status == "analyzed":
                    report["analyzed_at"] = self._now_iso()
                
                self._write_json(self.reports_file, reports)
                return report
        
        raise ValueError(f"Report with id {report_id} not found")
    
    def get_analysis_by_report(self, report_id: str) -> Optional[dict]:
        """
        获取研报分析结果
        
        Args:
            report_id: 研报ID
        
        Returns:
            分析结果数据，不存在或无分析结果返回None
        """
        report = self.get_report_by_id(report_id)
        
        if report is None:
            return None
        
        return report.get("analysis")


# 全局存储实例
_storage_instance: Optional[Storage] = None


def get_storage() -> Storage:
    """获取全局Storage实例（单例模式）"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = Storage()
    return _storage_instance


def init_storage(data_dir: str = None) -> Storage:
    """初始化存储实例"""
    global _storage_instance
    _storage_instance = Storage(data_dir)
    return _storage_instance
