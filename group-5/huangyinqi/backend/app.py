"""Flask application entry point."""

from flask import Flask
from flask_cors import CORS
from agent_bp import agent_bp


def create_app(data_dir=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    if data_dir:
        app.config["DATA_DIR"] = data_dir

    app.register_blueprint(agent_bp, url_prefix="/api/v1/agent")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
