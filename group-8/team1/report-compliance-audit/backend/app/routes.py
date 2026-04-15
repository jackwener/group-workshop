from flask import Blueprint, jsonify
import uuid

compliance_bp = Blueprint("compliance", __name__)


def _trace_id():
    return f"tr_{uuid.uuid4().hex[:12]}"


@compliance_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "traceId": _trace_id(),
        "status": "healthy",
        "service": "report-compliance-audit"
    }), 200


@compliance_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    """Get system capabilities"""
    return jsonify({
        "traceId": _trace_id(),
        "service": "Report Compliance Audit",
        "version": "1.0.0",
        "features": [
            "report-upload",
            "compliance-check",
            "audit-trail"
        ]
    }), 200
