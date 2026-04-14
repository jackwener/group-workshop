"""Response utilities for API standardization."""
from flask import jsonify


def success_response(data=None, message="success", code=200):
    """
    Return a standardized success response.
    
    Format: {code, message, data}
    """
    response = {
        "code": code,
        "message": message,
        "data": data if data is not None else {}
    }
    return jsonify(response), code


def error_response(message, error_code, http_status=400, error_detail=None):
    """
    Return a standardized error response.
    
    Format: {code, message, error}
    """
    response = {
        "code": error_code,
        "message": message,
        "error": error_detail if error_detail else message
    }
    return jsonify(response), http_status


def created_response(data, message="created"):
    """Return a 201 created response."""
    return success_response(data=data, message=message, code=201)
