"""Flask Application Factory."""
import os
from flask import Flask
from flask_cors import CORS

from app.api.sessions import sessions_bp
from app.api.analysis import analysis_bp
from app.api.reports import reports_bp
from app.api.health import health_bp
from app.utils.security import add_security_headers


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['DATA_DIR'] = os.path.join(os.path.dirname(__file__), '..', 'data')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    
    if test_config:
        app.config.update(test_config)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints with /api/v1 prefix
    app.register_blueprint(sessions_bp, url_prefix='/api/v1')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1')
    app.register_blueprint(reports_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    
    # Add security headers
    app.after_request(add_security_headers)
    
    # Ensure data directories exist
    ensure_data_dirs(app.config['DATA_DIR'])
    
    return app


def ensure_data_dirs(data_dir):
    """Ensure all data directories exist."""
    dirs = ['sessions', 'analysis', 'reports', 'uploads']
    for d in dirs:
        path = os.path.join(data_dir, d)
        os.makedirs(path, exist_ok=True)
