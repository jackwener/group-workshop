import uuid

from flask import jsonify, request


def generate_trace_id():
    trace_id = request.headers.get("X-Trace-Id")
    if trace_id:
        return trace_id
    return f"tr_{uuid.uuid4().hex}"


def ok(status_code=200, **kwargs):
    response = {"traceId": generate_trace_id()}
    response.update(kwargs)
    return jsonify(response), status_code


def error(code, message, details=None, status=400):
    return jsonify({
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": generate_trace_id(),
        }
    }), status
