"""Analysis Service for report and stock analysis."""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from app.models.analysis import Analysis
from app.models.message import Message
from app.dao.analysis_dao import AnalysisDAO
from app.dao.session_dao import SessionDAO
from app.services.llm_service import get_llm_service
from app.utils.security import AuditLogger


class FileProcessor:
    """Process uploaded files (PDF/Word)."""
    
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def save_file(file, upload_dir: str) -> Tuple[str, str]:
        """Save uploaded file and return (filename, filepath)."""
        from app.utils.security import sanitize_filename
        
        filename = sanitize_filename(file.filename)
        if not filename:
            raise ValueError("Invalid filename")
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        return filename, filepath
    
    @staticmethod
    def extract_text(filepath: str) -> str:
        """Extract text from PDF or Word file."""
        ext = filepath.rsplit('.', 1)[1].lower()
        
        if ext == 'pdf':
            return FileProcessor._extract_pdf(filepath)
        elif ext in ('doc', 'docx'):
            return FileProcessor._extract_word(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    @staticmethod
    def _extract_pdf(filepath: str) -> str:
        """Extract text from PDF."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract PDF: {e}")
    
    @staticmethod
    def _extract_word(filepath: str) -> str:
        """Extract text from Word document."""
        try:
            from docx import Document
            doc = Document(filepath)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract Word document: {e}")


class AnalysisService:
    """Service for report and stock analysis."""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.upload_dir = os.path.join(data_dir, 'uploads')
        os.makedirs(self.upload_dir, exist_ok=True)
        
        self.analysis_dao = AnalysisDAO(data_dir)
        self.session_dao = SessionDAO(data_dir)
        self.llm_service = get_llm_service()
    
    def analyze_report(self, session_id: str, files: List, 
                       extract_keywords: bool = True,
                       compare_reports: bool = False) -> Dict[str, Any]:
        """
        Analyze uploaded report files.
        
        Aligned with 06-功能规格说明.md §3.1 and 09-API接口规格.md §4.1
        """
        start_time = datetime.now()
        
        # Validate session
        if not self.session_dao.session_exists(session_id):
            from app.utils.errors import SessionNotFoundError
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        # Save files and extract text
        file_results = []
        for file in files:
            filename, filepath = FileProcessor.save_file(file, self.upload_dir)
            text = FileProcessor.extract_text(filepath)
            file_results.append({
                "filename": filename,
                "filepath": filepath,
                "text": text
            })
        
        # Create analysis record
        input_data = {
            "files": [f["filename"] for f in file_results],
            "extract_keywords": extract_keywords,
            "compare_reports": compare_reports
        }
        analysis = self.analysis_dao.create_analysis(session_id, "report", input_data)
        
        # Analyze each file
        reports = []
        for file_result in file_results:
            result, fallback_level, llm_status = self.llm_service.analyze_report(
                file_result["text"], extract_keywords
            )
            result["filename"] = file_result["filename"]
            reports.append(result)
        
        # Compare reports if multiple and compare_reports=True
        comparison = None
        if len(reports) > 1 and compare_reports:
            comparison = self._compare_reports(reports)
        
        # Build output
        output_data = {
            "reports": reports,
            "comparison": comparison
        }
        
        # Complete analysis
        self.analysis_dao.complete_analysis(analysis.id, output_data)
        
        # Create assistant message
        summary = self._build_report_summary(reports, comparison)
        message = Message.create(
            message_id=f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            session_id=session_id,
            role="assistant",
            content=summary,
            msg_type="analysis",
            attachments=[{"analysis_id": analysis.id}]
        )
        self.session_dao.add_message(session_id, message)
        
        # Audit log
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        AuditLogger.log("analysis.report", analysis.id, "success", duration_ms=duration)
        
        return {
            "analysis_id": analysis.id,
            "status": "completed",
            "reports": reports,
            "comparison": comparison,
            "fallback_level": fallback_level,
            "llm_status": llm_status
        }
    
    def analyze_stock(self, session_id: str, stock_code: str,
                      stock_name: Optional[str] = None,
                      analysis_type: str = "full") -> Dict[str, Any]:
        """
        Analyze stock data.
        
        Aligned with 06-功能规格说明.md §3.2 and 09-API接口规格.md §4.2
        """
        start_time = datetime.now()
        
        # Validate session
        if not self.session_dao.session_exists(session_id):
            from app.utils.errors import SessionNotFoundError
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        # Validate stock code
        from app.utils.security import validate_stock_code
        if not validate_stock_code(stock_code):
            from app.utils.errors import FormatError
            raise FormatError("Stock code must be 6 digits")
        
        # Fetch stock data (placeholder - integrate with actual data source)
        stock_data = self._fetch_stock_data(stock_code, stock_name)
        
        # Create analysis record
        input_data = {
            "stock_code": stock_code,
            "stock_name": stock_name or "",
            "analysis_type": analysis_type
        }
        analysis = self.analysis_dao.create_analysis(session_id, "stock", input_data)
        
        # Analyze with LLM
        result, fallback_level, llm_status = self.llm_service.analyze_stock(stock_data)
        
        # Build output
        output_data = {
            "stock_code": stock_code,
            "stock_name": stock_name or result.get("stock_name", ""),
            "financial_indicators": result.get("financial_indicators", {}),
            "report_summary": result.get("report_summary", ""),
            "comprehensive_score": result.get("comprehensive_score", 0),
            "risk_level": result.get("risk_level", "medium"),
            "recommendation": result.get("recommendation", "hold"),
            "analysis_time": datetime.utcnow().isoformat() + "Z",
            "accuracy": result.get("accuracy", 0.9)
        }
        
        # Complete analysis
        self.analysis_dao.complete_analysis(analysis.id, output_data, output_data.get("accuracy"))
        
        # Create assistant message
        summary = self._build_stock_summary(output_data)
        message = Message.create(
            message_id=f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            session_id=session_id,
            role="assistant",
            content=summary,
            msg_type="analysis",
            attachments=[{"analysis_id": analysis.id}]
        )
        self.session_dao.add_message(session_id, message)
        
        # Audit log
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        AuditLogger.log("analysis.stock", analysis.id, "success", duration_ms=duration)
        
        return {
            "analysis_id": analysis.id,
            **output_data,
            "fallback_level": fallback_level,
            "llm_status": llm_status
        }
    
    def _compare_reports(self, reports: List[Dict]) -> Dict[str, Any]:
        """Compare multiple reports and calculate similarity/consistency."""
        # Simple comparison logic (can be enhanced with actual NLP)
        ratings = [r.get("rating", "") for r in reports]
        consistency = "观点基本一致" if len(set(ratings)) == 1 else "观点存在分歧"
        
        return {
            "similarity": 0.75,  # Placeholder
            "consistency": consistency,
            "rating_distribution": {r: ratings.count(r) for r in set(ratings)}
        }
    
    def _fetch_stock_data(self, stock_code: str, stock_name: Optional[str]) -> Dict[str, Any]:
        """Fetch stock data from data source."""
        # Placeholder - integrate with actual data source
        # In production, this should call internal data APIs
        return {
            "stock_code": stock_code,
            "stock_name": stock_name or f"股票{stock_code}",
            "financial_data": {
                "revenue": 1500000000,
                "profit": 450000000,
                "roe": 12.5,
                "pe": 8.5,
                "pb": 1.2
            },
            "report_summary": "多家机构给予买入评级..."
        }
    
    def _build_report_summary(self, reports: List[Dict], comparison: Optional[Dict]) -> str:
        """Build summary text for report analysis."""
        lines = ["研报分析结果："]
        for i, report in enumerate(reports, 1):
            lines.append(f"\n【研报{i}】{report.get('filename', '')}")
            lines.append(f"标题：{report.get('title', '')}")
            lines.append(f"摘要：{report.get('summary', '')}")
            lines.append(f"评级：{report.get('rating', '')}")
        
        if comparison:
            lines.append(f"\n【比对分析】")
            lines.append(f"观点一致性：{comparison.get('consistency', '')}")
        
        return "\n".join(lines)
    
    def _build_stock_summary(self, output_data: Dict) -> str:
        """Build summary text for stock analysis."""
        return f"""股票分析报告：

股票代码：{output_data['stock_code']}
股票名称：{output_data['stock_name']}
综合评分：{output_data['comprehensive_score']}
风险等级：{output_data['risk_level']}
投资建议：{output_data['recommendation']}

财务指标：
- 营收：{output_data['financial_indicators'].get('revenue', 0)}
- 净利润：{output_data['financial_indicators'].get('profit', 0)}
- ROE：{output_data['financial_indicators'].get('roe', 0)}%
- PE：{output_data['financial_indicators'].get('pe', 0)}
- PB：{output_data['financial_indicators'].get('pb', 0)}

研报摘要：{output_data['report_summary']}
"""
