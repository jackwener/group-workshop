import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from backend.storage import Storage
from backend.agent import CoPawAgent
from backend.blueprints.agent_bp import agent_bp, init_bp

load_dotenv()


def create_app(data_dir=None):
    app = Flask(__name__)
    CORS(app)

    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), "data")

    s = Storage(data_dir=data_dir)
    a = CoPawAgent(s)
    init_bp(s, a)

    app.register_blueprint(agent_bp)

    @app.route("/")
    def index():
        return jsonify({
            "service": "投研问答助手 API",
            "version": "1.0.0",
            "endpoints": {
                "capabilities": "GET /api/v1/agent/capabilities",
                "sessions": "GET /api/v1/agent/sessions",
                "create_session": "POST /api/v1/agent/sessions",
                "delete_session": "DELETE /api/v1/agent/sessions/<id>",
                "ask": "POST /api/v1/agent/ask",
                "records": "GET /api/v1/agent/sessions/<id>/records",
            }
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
