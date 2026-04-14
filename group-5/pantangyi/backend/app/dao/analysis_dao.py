"""Analysis Data Access Object."""
import os
import json
import glob
from datetime import datetime
from typing import List, Optional

from app.models.analysis import Analysis


class AnalysisDAO:
    """DAO for Analysis CRUD operations."""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.analysis_dir = os.path.join(data_dir, 'analysis')
        os.makedirs(self.analysis_dir, exist_ok=True)
    
    def _get_analysis_path(self, analysis_id: str) -> str:
        """Get file path for an analysis."""
        return os.path.join(self.analysis_dir, f"{analysis_id}.json")
    
    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID: ana_YYYYMMDD{序号}."""
        today = datetime.now().strftime("%Y%m%d")
        pattern = os.path.join(self.analysis_dir, f"ana_{today}*.json")
        existing = glob.glob(pattern)
        seq = len(existing) + 1
        return f"ana_{today}{seq:04d}"
    
    def create_analysis(self, session_id: str, analysis_type: str, 
                        input_data: dict) -> Analysis:
        """
        Create a new analysis task.
        Aligned with 10-数据模型与存储规格.md §2.3
        """
        analysis_id = self._generate_analysis_id()
        analysis = Analysis.create(analysis_id, session_id, analysis_type, input_data)
        
        analysis_path = self._get_analysis_path(analysis_id)
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis.to_dict(), f, ensure_ascii=False, indent=2)
        
        return analysis
    
    def get_analysis(self, analysis_id: str) -> Optional[Analysis]:
        """Get analysis by ID."""
        analysis_path = self._get_analysis_path(analysis_id)
        if not os.path.exists(analysis_path):
            return None
        
        with open(analysis_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Analysis.from_dict(data)
    
    def update_analysis(self, analysis: Analysis) -> bool:
        """Update analysis data."""
        analysis_path = self._get_analysis_path(analysis.id)
        if not os.path.exists(analysis_path):
            return False
        
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis.to_dict(), f, ensure_ascii=False, indent=2)
        
        return True
    
    def complete_analysis(self, analysis_id: str, output_data: dict, 
                          accuracy: Optional[float] = None) -> bool:
        """Mark analysis as completed."""
        analysis = self.get_analysis(analysis_id)
        if not analysis:
            return False
        
        analysis.complete(output_data, accuracy)
        return self.update_analysis(analysis)
    
    def fail_analysis(self, analysis_id: str, error_msg: str) -> bool:
        """Mark analysis as failed."""
        analysis = self.get_analysis(analysis_id)
        if not analysis:
            return False
        
        analysis.fail(error_msg)
        return self.update_analysis(analysis)
    
    def list_by_session(self, session_id: str) -> List[Analysis]:
        """List all analyses for a session."""
        pattern = os.path.join(self.analysis_dir, "ana_*.json")
        all_files = glob.glob(pattern)
        
        analyses = []
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get("session_id") == session_id:
                    analyses.append(Analysis.from_dict(data))
            except (json.JSONDecodeError, IOError):
                continue
        
        # Sort by created_at desc
        analyses.sort(key=lambda a: a.created_at, reverse=True)
        return analyses
    
    def delete_by_session(self, session_id: str) -> int:
        """Delete all analyses for a session (cascade delete)."""
        analyses = self.list_by_session(session_id)
        count = 0
        for analysis in analyses:
            analysis_path = self._get_analysis_path(analysis.id)
            if os.path.exists(analysis_path):
                os.remove(analysis_path)
                count += 1
        return count
