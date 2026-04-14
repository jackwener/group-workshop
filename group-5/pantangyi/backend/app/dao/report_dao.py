"""Report Data Access Object."""
import os
import json
from datetime import datetime
from typing import Optional

from app.models.report import Report


class ReportDAO:
    """DAO for Report CRUD operations."""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.reports_dir = os.path.join(data_dir, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def _get_report_path(self, report_id: str) -> str:
        """Get file path for a report JSON metadata."""
        return os.path.join(self.reports_dir, f"{report_id}.json")
    
    def _get_pdf_path(self, report_id: str) -> str:
        """Get file path for a report PDF."""
        return os.path.join(self.reports_dir, f"{report_id}.pdf")
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID: rpt_YYYYMMDD{序号}."""
        today = datetime.now().strftime("%Y%m%d")
        import glob
        pattern = os.path.join(self.reports_dir, f"rpt_{today}*.json")
        existing = glob.glob(pattern)
        seq = len(existing) + 1
        return f"rpt_{today}{seq:04d}"
    
    def create_report(self, analysis_id: str, session_id: str, title: str,
                      report_type: str, content: dict, 
                      pdf_content: Optional[bytes] = None) -> Report:
        """
        Create a new report.
        Aligned with 10-数据模型与存储规格.md §2.4
        """
        report_id = self._generate_report_id()
        
        # Save PDF if provided
        pdf_path = None
        if pdf_content:
            pdf_path = self._get_pdf_path(report_id)
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)
        
        # Create report metadata
        file_path = f"reports/{report_id}.pdf" if pdf_path else ""
        report = Report.create(report_id, analysis_id, session_id, 
                               title, report_type, content, file_path)
        
        # Save metadata
        report_path = self._get_report_path(report_id)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        return report
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """Get report by ID."""
        report_path = self._get_report_path(report_id)
        if not os.path.exists(report_path):
            return None
        
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Report.from_dict(data)
    
    def get_report_pdf_path(self, report_id: str) -> Optional[str]:
        """Get PDF file path for a report."""
        pdf_path = self._get_pdf_path(report_id)
        if os.path.exists(pdf_path):
            return pdf_path
        return None
    
    def get_report_json(self, report_id: str) -> Optional[dict]:
        """Get report content as JSON."""
        report = self.get_report(report_id)
        if not report:
            return None
        return report.content
