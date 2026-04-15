"""Health Check API Routes."""
from flask import Blueprint, current_app
from datetime import datetime

from app.utils.response import success_response, error_response
from app.services.llm_service import get_llm_service
from app.dao.session_dao import SessionDAO

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    GET /health - Health check endpoint.
    
    Aligned with 09-API接口规格.md §5.2 (API-009)
    """
    try:
        # Check data directory
        data_dir = current_app.config['DATA_DIR']
        dao = SessionDAO(data_dir)
        
        # Try to list sessions (tests file system access)
        try:
            _, _ = dao.list_sessions(limit=1)
            database_status = "connected"
        except Exception:
            database_status = "error"
        
        # Check LLM service
        llm_service = get_llm_service()
        llm_health = llm_service.health_check()
        
        # Determine overall status
        if database_status == "connected" and llm_health["current"] in ["primary", "fallback-1"]:
            status = "healthy"
            http_code = 200
        elif database_status == "connected":
            status = "degraded"
            http_code = 503
        else:
            status = "unhealthy"
            http_code = 503
        
        response_data = {
            "status": status,
            "version": "v1.0.0",
            "services": {
                "llm": llm_health["current"],
                "database": database_status
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if status == "degraded":
            response_data["fallback_level"] = 2 if llm_health["current"] == "demo" else 1
        
        response = success_response(response_data)
        return response[0], http_code
    
    except Exception as e:
        return error_response("Health check failed", 500, 500, str(e))
