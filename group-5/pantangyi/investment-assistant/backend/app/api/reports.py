"""Reports API Routes."""
from flask import Blueprint, request, current_app, send_file

from app.utils.response import success_response, error_response
from app.utils.errors import APIError, ReportNotFoundError
from app.services.report_service import ReportService

reports_bp = Blueprint('reports', __name__)


def get_report_service():
    """Get ReportService instance."""
    return ReportService(current_app.config['DATA_DIR'])


@reports_bp.route('/reports/<report_id>/download', methods=['GET'])
def download_report(report_id):
    """
    GET /reports/{id}/download - Download report.
    
    Aligned with 09-API接口规格.md §5.1 (API-008)
    """
    try:
        # Get format parameter
        format = request.args.get('format', 'pdf')
        
        if format not in ['pdf', 'json']:
            return error_response("Invalid format", 400002, 400, "Format must be pdf or json")
        
        # Get report
        service = get_report_service()
        content, content_type, filename = service.download_report(report_id, format)
        
        # Send file
        from io import BytesIO
        return send_file(
            BytesIO(content),
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))


@reports_bp.route('/reports', methods=['POST'])
def generate_report():
    """
    POST /reports - Generate a new report from analysis.
    
    Internal API for report generation.
    """
    try:
        data = request.get_json() or {}
        analysis_id = data.get('analysis_id', '')
        
        if not analysis_id:
            return error_response("analysis_id is required", 400001, 400)
        
        service = get_report_service()
        report = service.generate_report(analysis_id)
        
        return success_response(report.to_dict())
    
    except APIError as e:
        return error_response(e.message, e.error_code, e.http_status, e.detail)
    except Exception as e:
        return error_response("Internal server error", 500, 500, str(e))
