"""Report data model."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any


@dataclass
class Report:
    """
    Report entity aligned with 10-数据模型与存储规格.md §2.4
    
    Storage: data/reports/{report_id}.json + {report_id}.pdf
    """
    id: str
    analysis_id: str
    session_id: str
    title: str
    type: str  # report/stock
    content: Dict[str, Any]
    file_path: str
    created_at: str
    
    @classmethod
    def create(cls, report_id: str, analysis_id: str, session_id: str,
               title: str, report_type: str, content: Dict[str, Any],
               file_path: str):
        """Create a new report."""
        now = datetime.utcnow().isoformat() + "Z"
        return cls(
            id=report_id,
            analysis_id=analysis_id,
            session_id=session_id,
            title=title,
            type=report_type,
            content=content,
            file_path=file_path,
            created_at=now
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Report":
        """Create Report from dictionary."""
        return cls(**data)
