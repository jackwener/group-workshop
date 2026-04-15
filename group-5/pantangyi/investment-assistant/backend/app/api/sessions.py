"""Session API Routes."""
from flask import Blueprint, request, current_app

from app.utils.response import success_response, created_response, error_response
from app.utils.errors import APIError, SessionNotFoundError, ValidationError, FormatError
from app.utils.security import validate_title, validate_pagination_params, AuditLogger
from app.dao.session_dao import SessionDAO
from app.services.session_service import SessionService

sessions_bp = Blueprint('sessions', __name__)


def get_session_dao():
    """Get SessionDAO instance."""
    return SessionDAO(current_app.config['DATA_DIR'])


def get_session_service():
    """Get SessionService instance."""
    return SessionService(current_app.config['DATA_DIR'])


@sessions_bp.route('/sessions', methods=['POST'])
def create_session():
    """
    POST /sessions - Create a new session.
    
    Aligned with 09-API接口规格.md §3.1 (API-001)
    """
    try:
        data = request.get_json() or {}
        
        title = data.get('title', '新会话')
        session_type = data.get('type', 'general')
        
        # Validate title
        if not validate_title(title):
            raise FormatError("Title must be <= 100 characters")
        
        # Create session
        dao = get_session_dao()
        session = dao.create_session(title=title, session_type=session_type)
        
        # Audit log
        AuditLogger.log("session.create", session.id, "success")
        
        return created_response(session.to_dict())
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))


@sessions_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """
    GET /sessions - List sessions.
    
    Aligned with 09-API接口规格.md §3.2 (API-002)
    """
    try:
        # Get pagination params
        limit = request.args.get('limit', 5, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate pagination
        limit, offset = validate_pagination_params(limit, offset)
        
        # List sessions
        dao = get_session_dao()
        sessions, total = dao.list_sessions(limit=limit, offset=offset)
        
        return success_response({
            "total": total,
            "items": [s.to_dict() for s in sessions]
        })
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))


@sessions_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    DELETE /sessions/{id} - Delete a session.
    
    Aligned with 09-API接口规格.md §3.3 (API-003)
    """
    try:
        dao = get_session_dao()
        
        # Check if exists
        if not dao.get_session(session_id):
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        # Delete session
        dao.delete_session(session_id)
        
        # Audit log
        AuditLogger.log("session.delete", session_id, "success")
        
        return success_response(None, "success")
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))


@sessions_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    GET /sessions/{id} - Get session details with messages.
    
    Aligned with 09-API接口规格.md §3.4 (API-004)
    """
    try:
        dao = get_session_dao()
        
        # Get session with messages
        session, messages = dao.get_session_with_messages(session_id)
        
        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        # Build response
        response_data = session.to_dict()
        response_data['messages'] = messages
        
        return success_response(response_data)
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))


@sessions_bp.route('/sessions/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """
    POST /sessions/{id}/messages - Send a message.
    
    Aligned with 09-API接口规格.md §4.3 (API-007)
    """
    try:
        data = request.get_json() or {}
        
        content = data.get('content', '')
        msg_type = data.get('type', 'text')
        
        # Validate content
        if not content:
            raise ValidationError("Content is required")
        
        # Send message
        service = get_session_service()
        result = service.send_message(session_id, content, msg_type)
        
        return success_response(result)
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))
