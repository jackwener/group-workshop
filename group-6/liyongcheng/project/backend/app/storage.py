"""存储层模块 - JSON文件存储实现"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any

from app.config import config


class Storage:
    """JSON文件存储类"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        初始化存储层
        
        Args:
            data_dir: 数据目录路径，默认使用配置中的DATA_DIR
        """
        self.data_dir = data_dir or config.DATA_DIR
        self.reports_file = self.data_dir / 'reports.json'
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.reports_file.exists():
            self._write_reports([])
    
    def _read_reports(self) -> List[Dict[str, Any]]:
        """读取所有研报数据"""
        try:
            with open(self.reports_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_reports(self, reports: List[Dict[str, Any]]) -> None:
        """写入所有研报数据"""
        with open(self.reports_file, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self) -> str:
        """生成研报ID: rpt_{uuid}"""
        return f"rpt_{uuid.uuid4().hex[:12]}"
    
    def _get_timestamp(self) -> str:
        """获取当前UTC时间戳"""
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # ==================== 研报管理 ====================
    
    def create_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新研报记录
        
        Args:
            report_data: 研报数据字典
            
        Returns:
            创建的研报记录（含自动生成的ID和时间戳）
        """
        reports = self._read_reports()
        
        now = self._get_timestamp()
        report = {
            'id': self._generate_id(),
            'title': report_data.get('title', ''),
            'subject_name': report_data.get('subject_name', ''),
            'subject_code': report_data.get('subject_code', ''),
            'author': report_data.get('author', ''),
            'rating': report_data.get('rating', ''),
            'trend': report_data.get('trend', 'neutral'),
            'target_price': report_data.get('target_price'),
            'summary': report_data.get('summary', ''),
            'file_path': report_data.get('file_path', ''),
            'created_at': now,
            'updated_at': now,
            'parse_status': report_data.get('parse_status', 'success'),
        }
        
        reports.append(report)
        self._write_reports(reports)
        return report
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取研报详情
        
        Args:
            report_id: 研报ID
            
        Returns:
            研报数据字典，不存在返回None
        """
        reports = self._read_reports()
        for report in reports:
            if report['id'] == report_id:
                return report
        return None
    
    def get_reports(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取研报列表（支持分页和筛选）
        
        Args:
            filters: 筛选条件，包含：
                - page: 页码（默认1）
                - page_size: 每页数量（默认20）
                - subject_code: 股票代码筛选
                - author: 券商筛选
                - keyword: 关键词搜索（标题）
                
        Returns:
            分页数据字典
        """
        filters = filters or {}
        page = filters.get('page', 1)
        page_size = filters.get('page_size', 20)
        subject_code = filters.get('subject_code', '')
        author = filters.get('author', '')
        keyword = filters.get('keyword', '')
        
        reports = self._read_reports()
        
        # 筛选
        filtered = []
        for report in reports:
            if subject_code and report.get('subject_code') != subject_code:
                continue
            if author and report.get('author') != author:
                continue
            if keyword and keyword.lower() not in report.get('title', '').lower():
                continue
            filtered.append(report)
        
        # 排序（按创建时间倒序）
        filtered.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # 分页
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        items = filtered[start:end]
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': items,
        }
    
    def update_report(self, report_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新研报信息
        
        Args:
            report_id: 研报ID
            updates: 更新数据
            
        Returns:
            更新后的研报数据，不存在返回None
        """
        reports = self._read_reports()
        
        for i, report in enumerate(reports):
            if report['id'] == report_id:
                # 更新字段
                for key, value in updates.items():
                    if key not in ('id', 'created_at'):
                        report[key] = value
                report['updated_at'] = self._get_timestamp()
                reports[i] = report
                self._write_reports(reports)
                return report
        
        return None
    
    def delete_report(self, report_id: str) -> bool:
        """
        删除研报记录
        
        Args:
            report_id: 研报ID
            
        Returns:
            删除成功返回True，不存在返回False
        """
        reports = self._read_reports()
        
        for i, report in enumerate(reports):
            if report['id'] == report_id:
                # 删除关联文件
                file_path = report.get('file_path', '')
                if file_path:
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except Exception:
                        pass
                
                # 删除记录
                reports.pop(i)
                self._write_reports(reports)
                return True
        
        return False
    
    def get_reports_by_subject(self, subject_code: str) -> List[Dict[str, Any]]:
        """
        根据股票代码获取所有研报
        
        Args:
            subject_code: 股票代码
            
        Returns:
            研报列表
        """
        reports = self._read_reports()
        filtered = [r for r in reports if r.get('subject_code') == subject_code]
        filtered.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return filtered
    
    # ==================== 对比分析 ====================
    
    def compare_reports(self, subject_code: str, report_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        对比同一股票的多份研报
        
        Args:
            subject_code: 股票代码
            report_ids: 指定对比的研报ID列表（为空则对比该股票全部研报）
            
        Returns:
            对比数据字典
        """
        if report_ids:
            reports = [self.get_report(rid) for rid in report_ids]
            reports = [r for r in reports if r is not None]
        else:
            reports = self.get_reports_by_subject(subject_code)
        
        # 获取研究对象名称
        subject_name = reports[0].get('subject_name', '') if reports else ''
        
        # 构建对比列表
        comparison = []
        for report in reports:
            comparison.append({
                'report_id': report['id'],
                'author': report.get('author', ''),
                'rating': report.get('rating', ''),
                'trend': report.get('trend', 'neutral'),
                'target_price': report.get('target_price'),
                'summary': report.get('summary', '')[:200],  # 最多200字
                'publish_date': report.get('created_at', '')[:10],
            })
        
        return {
            'subject_name': subject_name,
            'subject_code': subject_code,
            'report_count': len(comparison),
            'comparison': comparison,
        }
    
    # ==================== 统计查询 ====================
    
    def count_reports(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计研报数量"""
        result = self.get_reports(filters)
        return result['total']
    
    def get_subject_list(self) -> List[Dict[str, str]]:
        """获取所有研究对象（去重）"""
        reports = self._read_reports()
        seen = set()
        subjects = []
        for report in reports:
            code = report.get('subject_code', '')
            if code and code not in seen:
                seen.add(code)
                subjects.append({
                    'subject_code': code,
                    'subject_name': report.get('subject_name', ''),
                })
        return subjects
    
    def get_author_list(self) -> List[str]:
        """获取所有券商（去重）"""
        reports = self._read_reports()
        authors = set()
        for report in reports:
            author = report.get('author', '')
            if author:
                authors.add(author)
        return sorted(list(authors))


# 全局存储实例
storage = Storage()
