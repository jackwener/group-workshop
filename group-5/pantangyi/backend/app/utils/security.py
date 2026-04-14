"""Security utilities for the application."""
import html
import re
from datetime import datetime


def add_security_headers(response):
    """Add security headers to all responses."""
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # XSS Protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # HSTS (only in production with HTTPS)
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


def sanitize_html(text):
    """Sanitize HTML content to prevent XSS."""
    if not text:
        return text
    return html.escape(text)


def validate_stock_code(code):
    """Validate stock code format (6 digits)."""
    if not code:
        return False
    return bool(re.match(r'^\d{6}$', code))


def validate_title(title):
    """Validate session title (max 100 chars, no XSS)."""
    if not title:
        return True  # Optional field
    if len(title) > 100:
        return False
    return True


def validate_message_content(content):
    """Validate message content (max 5000 chars)."""
    if not content:
        return False
    if len(content) > 5000:
        return False
    return True


def validate_pagination_params(limit, offset):
    """Validate pagination parameters."""
    try:
        limit = int(limit) if limit else 5
        offset = int(offset) if offset else 0
        
        if limit < 1 or limit > 20:
            limit = 5
        if offset < 0:
            offset = 0
            
        return limit, offset
    except (ValueError, TypeError):
        return 5, 0


def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal."""
    if not filename:
        return None
    # Remove path components
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    # Remove special characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    return filename


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class AuditLogger:
    """Audit logger for security events."""
    
    @staticmethod
    def log(action, resource, result="success", user_id=None, ip=None, duration_ms=None):
        """Log an audit event."""
        # In production, this should write to a proper audit log file
        # For now, we'll use the standard logger
        import logging
        logger = logging.getLogger('audit')
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "resource": resource,
            "result": result,
            "user_id": user_id or "anonymous",
            "ip": ip or "unknown",
            "duration_ms": duration_ms
        }
        
        logger.info(f"AUDIT: {log_entry}")
