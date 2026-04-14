"""Message data model."""
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Attachment:
    """Attachment metadata."""
    filename: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Attachment":
        return cls(**data)


@dataclass
class Message:
    """
    Message entity aligned with 10-数据模型与存储规格.md §2.2
    
    Storage: data/sessions/{session_id}_messages.json
    """
    id: str
    session_id: str
    role: str  # user/assistant/system
    content: str
    type: str  # text/file/analysis
    timestamp: str
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def create(cls, message_id: str, session_id: str, role: str, 
               content: str, msg_type: str = "text", 
               attachments: Optional[List[Dict]] = None):
        """Create a new message with default values."""
        now = datetime.utcnow().isoformat() + "Z"
        return cls(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            type=msg_type,
            timestamp=now,
            attachments=attachments or []
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create Message from dictionary."""
        return cls(**data)


@dataclass
class MessageList:
    """Container for a list of messages."""
    messages: List[Message] = field(default_factory=list)
    
    def add_message(self, message: Message):
        """Add a message to the list."""
        self.messages.append(message)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {"messages": [m.to_dict() for m in self.messages]}
    
    @classmethod
    def from_dict(cls, data: dict) -> "MessageList":
        """Create MessageList from dictionary."""
        messages = [Message.from_dict(m) for m in data.get("messages", [])]
        return cls(messages=messages)
