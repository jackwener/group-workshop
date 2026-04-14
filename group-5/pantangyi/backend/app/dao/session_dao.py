"""Session Data Access Object."""
import os
import json
import glob
from datetime import datetime
from typing import List, Optional, Tuple

from app.models.session import Session
from app.models.message import MessageList, Message


class SessionDAO:
    """DAO for Session CRUD operations."""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.sessions_dir = os.path.join(data_dir, 'sessions')
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def _get_session_path(self, session_id: str) -> str:
        """Get file path for a session."""
        return os.path.join(self.sessions_dir, f"{session_id}.json")
    
    def _get_messages_path(self, session_id: str) -> str:
        """Get file path for session messages."""
        return os.path.join(self.sessions_dir, f"{session_id}_messages.json")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID: sess_YYYYMMDD{序号}."""
        today = datetime.now().strftime("%Y%m%d")
        pattern = os.path.join(self.sessions_dir, f"sess_{today}*.json")
        existing = glob.glob(pattern)
        # Filter out _messages.json files
        session_files = [f for f in existing if '_messages' not in f]
        seq = len(session_files) + 1
        return f"sess_{today}{seq:04d}"
    
    def create_session(self, title: str = "新会话", session_type: str = "general") -> Session:
        """
        Create a new session.
        Aligned with 10-数据模型与存储规格.md §2.1
        """
        session_id = self._generate_session_id()
        session = Session.create(session_id, title, session_type)
        
        # Save session
        session_path = self._get_session_path(session_id)
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Create empty messages file
        messages_path = self._get_messages_path(session_id)
        with open(messages_path, 'w', encoding='utf-8') as f:
            json.dump({"messages": []}, f, ensure_ascii=False, indent=2)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session_path = self._get_session_path(session_id)
        if not os.path.exists(session_path):
            return None
        
        with open(session_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Session.from_dict(data)
    
    def get_session_with_messages(self, session_id: str) -> Tuple[Optional[Session], List[dict]]:
        """Get session with its messages."""
        session = self.get_session(session_id)
        if not session:
            return None, []
        
        messages_path = self._get_messages_path(session_id)
        if not os.path.exists(messages_path):
            return session, []
        
        with open(messages_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return session, data.get("messages", [])
    
    def list_sessions(self, limit: int = 5, offset: int = 0) -> Tuple[List[Session], int]:
        """
        List sessions ordered by updated_at desc.
        Aligned with 10-数据模型与存储规格.md §4.2
        """
        pattern = os.path.join(self.sessions_dir, "sess_*.json")
        all_files = glob.glob(pattern)
        # Filter out _messages.json files
        session_files = [f for f in all_files if '_messages' not in f]
        
        sessions = []
        for file_path in session_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                sessions.append(Session.from_dict(data))
            except (json.JSONDecodeError, IOError):
                continue
        
        # Sort by updated_at desc
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        total = len(sessions)
        # Apply pagination
        paginated = sessions[offset:offset + limit]
        
        return paginated, total
    
    def update_session(self, session: Session) -> bool:
        """Update session data."""
        session_path = self._get_session_path(session.id)
        if not os.path.exists(session_path):
            return False
        
        session.update_timestamp()
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session (mark as deleted and cascade delete related data).
        Aligned with 10-数据模型与存储规格.md §5.1
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Mark as deleted
        session.status = "deleted"
        self.update_session(session)
        
        # Cascade delete: remove messages file
        messages_path = self._get_messages_path(session_id)
        if os.path.exists(messages_path):
            os.remove(messages_path)
        
        # Note: Analysis files are handled by AnalysisDAO
        
        return True
    
    def add_message(self, session_id: str, message: Message) -> bool:
        """Add a message to session."""
        messages_path = self._get_messages_path(session_id)
        
        # Load existing messages
        if os.path.exists(messages_path):
            with open(messages_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"messages": []}
        
        # Append new message
        data["messages"].append(message.to_dict())
        
        # Save
        with open(messages_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Update session message count
        session = self.get_session(session_id)
        if session:
            session.increment_message_count()
            self.update_session(session)
        
        return True
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists and is active."""
        session = self.get_session(session_id)
        return session is not None and session.status == "active"
