"""Analysis data model."""
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class Analysis:
    """
    Analysis entity aligned with 10-数据模型与存储规格.md §2.3
    
    Storage: data/analysis/{analysis_id}.json
    """
    id: str
    session_id: str
    type: str  # report/stock
    status: str  # processing/completed/failed
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    accuracy: Optional[float] = None
    error_msg: Optional[str] = None
    created_at: str = ""
    completed_at: Optional[str] = None
    
    @classmethod
    def create(cls, analysis_id: str, session_id: str, 
               analysis_type: str, input_data: Dict[str, Any]):
        """Create a new analysis task."""
        now = datetime.utcnow().isoformat() + "Z"
        return cls(
            id=analysis_id,
            session_id=session_id,
            type=analysis_type,
            status="processing",
            input_data=input_data,
            output_data={},
            created_at=now
        )
    
    def complete(self, output_data: Dict[str, Any], accuracy: Optional[float] = None):
        """Mark analysis as completed."""
        self.status = "completed"
        self.output_data = output_data
        self.accuracy = accuracy
        self.completed_at = datetime.utcnow().isoformat() + "Z"
    
    def fail(self, error_msg: str):
        """Mark analysis as failed."""
        self.status = "failed"
        self.error_msg = error_msg
        self.completed_at = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Analysis":
        """Create Analysis from dictionary."""
        return cls(**data)
