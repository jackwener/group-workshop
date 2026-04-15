import os
import json

from flask import Flask
from flask_cors import CORS

from config import Config
from blueprints.agent_bp import agent_bp


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or Config)

    CORS(app, origins=app.config.get("CORS_ORIGINS", ["http://localhost:5173"]))

    app.register_blueprint(agent_bp, url_prefix="/api/v1/agent")

    data_dir = app.config["DATA_DIR"]
    os.makedirs(data_dir, exist_ok=True)
    for filename in ["sessions.json", "qa_records.json", "upload_files.json", "reports.json"]:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    return app
