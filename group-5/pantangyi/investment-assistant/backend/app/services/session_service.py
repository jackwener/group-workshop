"""Session Service for message handling."""
from datetime import datetime
from typing import Dict, Any, Optional

from app.models.message import Message
from app.dao.session_dao import SessionDAO
from app.services.llm_service import get_llm_service
from app.utils.security import AuditLogger, validate_message_content
from app.utils.errors import ValidationError, SessionNotFoundError


class SessionService:
    """Service for session and message operations."""
    
    def __init__(self, data_dir: str):
        self.session_dao = SessionDAO(data_dir)
        self.llm_service = get_llm_service()
    
    def send_message(self, session_id: str, content: str, 
                     msg_type: str = "text") -> Dict[str, Any]:
        """
        Send a message in a session and get assistant response.
        
        Aligned with 06-功能规格说明.md §3.3 and 09-API接口规格.md §4.3
        """
        start_time = datetime.now()
        
        # Validate session
        if not self.session_dao.session_exists(session_id):
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        # Validate content
        if not content or not validate_message_content(content):
            raise ValidationError("Message content is required and must be <= 5000 chars")
        
        # Create user message
        user_msg = Message.create(
            message_id=f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}_user",
            session_id=session_id,
            role="user",
            content=content,
            msg_type=msg_type
        )
        self.session_dao.add_message(session_id, user_msg)
        
        # Get conversation history for context
        _, messages = self.session_dao.get_session_with_messages(session_id)
        
        # Generate assistant response
        response_text, fallback_level, llm_status = self.llm_service.chat(
            messages, context=""
        )
        
        # Create assistant message
        assistant_msg = Message.create(
            message_id=f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}_assistant",
            session_id=session_id,
            role="assistant",
            content=response_text,
            msg_type="text"
        )
        self.session_dao.add_message(session_id, assistant_msg)
        
        # Audit log
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        AuditLogger.log("message.send", session_id, "success", duration_ms=duration)
        
        return {
            "message_id": assistant_msg.id,
            "role": "assistant",
            "content": response_text,
            "timestamp": assistant_msg.timestamp,
            "fallback_level": fallback_level,
            "llm_status": llm_status
        }
    
    def get_session_messages(self, session_id: str) -> list:
        """Get all messages for a session."""
        _, messages = self.session_dao.get_session_with_messages(session_id)
        return messages
