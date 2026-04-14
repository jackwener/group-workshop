"""
Flask App 工厂 — 对齐 Spec 08 §2 分层架构
"""
import os
from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__)

    # CORS — 允许前端 dev server 跨域
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 配置
    app.config["DATA_DIR"] = os.environ.get("DATA_DIR", "./data")

    if test_config:
        app.config.update(test_config)

    # 注册蓝图
    from app.routes.agent_bp import agent_bp

    app.register_blueprint(agent_bp, url_prefix="/api/v1/agent")

    return app
