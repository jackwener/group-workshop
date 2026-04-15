from flask import Flask, jsonify
from flask_cors import CORS
from config import Config


def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(Config)

    # Register routes
    from app.routes import compliance_bp
    app.register_blueprint(compliance_bp, url_prefix="/api/v1/compliance")

    return app
