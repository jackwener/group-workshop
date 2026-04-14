"""Session data model."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Session:
    """
    Session entity aligned with 10-数据模型与存储规格.md §2.1
    
    Storage: data/sessions/{session_id}.json
    """
    id: str
    title: str
    type: str  # report/stock/general
    status: str  # active/archived/deleted
    created_at: str
    updated_at: str
    message_count: int = 0
    
    @classmethod
    def create(cls, session_id: str, title: str = "新会话", session_type: str = "general"):
        """Create a new session with default values."""
        now = datetime.utcnow().isoformat() + "Z"
        return cls(
            id=session_id,
            title=title,
            type=session_type,
            status="active",
            created_at=now,
            updated_at=now,
            message_count=0
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create Session from dictionary."""
        return cls(**data)
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow().isoformat() + "Z"
    
    def increment_message_count(self):
        """Increment message count."""
        self.message_count += 1
        self.update_timestamp()
