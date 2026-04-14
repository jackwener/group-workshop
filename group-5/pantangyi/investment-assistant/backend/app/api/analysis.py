"""Analysis API Routes."""
from flask import Blueprint, request, current_app

from app.utils.response import success_response, error_response
from app.utils.errors import APIError, SessionNotFoundError, FileTypeError, FormatError
from app.utils.security import allowed_file, validate_stock_code, AuditLogger
from app.dao.session_dao import SessionDAO
from app.services.analysis_service import AnalysisService

analysis_bp = Blueprint('analysis', __name__)


def get_analysis_service():
    """Get AnalysisService instance."""
    return AnalysisService(current_app.config['DATA_DIR'])


def get_session_dao():
    """Get SessionDAO instance."""
    return SessionDAO(current_app.config['DATA_DIR'])


@analysis_bp.route('/analysis/report', methods=['POST'])
def analyze_report():
    """
    POST /analysis/report - Analyze uploaded report files.
    
    Aligned with 09-API接口规格.md §4.1 (API-005)
    """
    try:
        # Get form data
        session_id = request.form.get('session_id', '')
        extract_keywords = request.form.get('extract_keywords', 'true').lower() == 'true'
        compare_reports = request.form.get('compare_reports', 'false').lower() == 'true'
        
        # Validate session
        if not session_id:
            raise FormatError("session_id is required")
        
        dao = get_session_dao()
        if not dao.session_exists(session_id):
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        # Get uploaded files
        files = request.files.getlist('files')
        if not files:
            raise FileTypeError("No files uploaded")
        
        # Validate file types
        for file in files:
            if not allowed_file(file.filename):
                raise FileTypeError(f"File type not supported: {file.filename}")
        
        # Analyze
        service = get_analysis_service()
        result = service.analyze_report(
            session_id=session_id,
            files=files,
            extract_keywords=extract_keywords,
            compare_reports=compare_reports
        )
        
        # Add LLM status header
        response = success_response(result)
        response[0].headers['X-LLM-Status'] = result.get('llm_status', 'primary')
        return response
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))


@analysis_bp.route('/analysis/stock', methods=['POST'])
def analyze_stock():
    """
    POST /analysis/stock - Analyze stock data.
    
    Aligned with 09-API接口规格.md §4.2 (API-006)
    """
    try:
        data = request.get_json() or {}
        
        session_id = data.get('session_id', '')
        stock_code = data.get('stock_code', '')
        stock_name = data.get('stock_name')
        analysis_type = data.get('analysis_type', 'full')
        
        # Validate session
        if not session_id:
            raise FormatError("session_id is required")
        
        dao = get_session_dao()
        if not dao.session_exists(session_id):
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        # Validate stock code
        if not stock_code:
            raise FormatError("stock_code is required")
        
        if not validate_stock_code(stock_code):
            raise FormatError("Stock code must be 6 digits")
        
        # Analyze
        service = get_analysis_service()
        result = service.analyze_stock(
            session_id=session_id,
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_type=analysis_type
        )
        
        # Add LLM status header
        response = success_response(result)
        response[0].headers['X-LLM-Status'] = result.get('llm_status', 'primary')
        return response
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))
