"""Unit tests for SessionDAO."""
import pytest
from app.models.session import Session
from app.models.message import Message


class TestSessionDAO:
    """Test cases for SessionDAO (TC-M01-060~062)."""
    
    def test_create_session(self, session_dao):
        """TC-M01-060: Session creation."""
        session = session_dao.create_session(title="测试会话", session_type="stock")
        
        assert session is not None
        assert session.id.startswith("sess_")
        assert session.title == "测试会话"
        assert session.type == "stock"
        assert session.status == "active"
        assert session.message_count == 0
        assert session.created_at is not None
        assert session.updated_at is not None
    
    def test_get_session(self, session_dao, sample_session):
        """TC-M01-060: Get session by ID."""
        retrieved = session_dao.get_session(sample_session.id)
        
        assert retrieved is not None
        assert retrieved.id == sample_session.id
        assert retrieved.title == sample_session.title
    
    def test_get_session_not_found(self, session_dao):
        """TC-M01-060: Get non-existent session."""
        result = session_dao.get_session("sess_nonexistent")
        assert result is None
    
    def test_list_sessions_ordering(self, session_dao):
        """TC-M01-061: List sessions ordered by updated_at desc."""
        # Create multiple sessions
        s1 = session_dao.create_session(title="会话1")
        s2 = session_dao.create_session(title="会话2")
        s3 = session_dao.create_session(title="会话3")
        
        # Update s1 to make it most recent
        s1.update_timestamp()
        session_dao.update_session(s1)
        
        # List sessions
        sessions, total = session_dao.list_sessions(limit=10, offset=0)
        
        assert total == 3
        assert sessions[0].id == s1.id  # Most recent first
        assert len(sessions) == 3
    
    def test_list_sessions_pagination(self, session_dao):
        """TC-M01-061: List sessions with pagination."""
        # Create 5 sessions
        for i in range(5):
            session_dao.create_session(title=f"会话{i}")
        
        # Test limit
        sessions, total = session_dao.list_sessions(limit=3, offset=0)
        assert len(sessions) == 3
        assert total == 5
        
        # Test offset
        sessions, total = session_dao.list_sessions(limit=3, offset=3)
        assert len(sessions) == 2
    
    def test_delete_session(self, session_dao, sample_session):
        """TC-M01-062: Delete session (mark as deleted)."""
        result = session_dao.delete_session(sample_session.id)
        
        assert result is True
        
        # Verify status changed
        session = session_dao.get_session(sample_session.id)
        assert session.status == "deleted"
    
    def test_delete_session_not_found(self, session_dao):
        """TC-M01-062: Delete non-existent session."""
        result = session_dao.delete_session("sess_nonexistent")
        assert result is False
    
    def test_session_exists(self, session_dao, sample_session):
        """TC-M01-062: Check session exists and is active."""
        assert session_dao.session_exists(sample_session.id) is True
        
        # Delete and check again
        session_dao.delete_session(sample_session.id)
        assert session_dao.session_exists(sample_session.id) is False
    
    def test_add_message(self, session_dao, sample_session):
        """TC-M01-063: Add message to session."""
        message = Message.create(
            message_id="msg_test_001",
            session_id=sample_session.id,
            role="user",
            content="测试消息",
            msg_type="text"
        )
        
        result = session_dao.add_message(sample_session.id, message)
        assert result is True
        
        # Verify message count updated
        session = session_dao.get_session(sample_session.id)
        assert session.message_count == 1
        
        # Verify messages file created
        _, messages = session_dao.get_session_with_messages(sample_session.id)
        assert len(messages) == 1
        assert messages[0]["content"] == "测试消息"
