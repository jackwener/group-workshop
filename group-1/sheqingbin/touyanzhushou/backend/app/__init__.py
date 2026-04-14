"""
投研问答助手 - Flask 应用工厂
"""
import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from .routes import agent_bp


def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["DATA_DIR"] = os.environ.get("DATA_DIR", "./data")
    
    # 确保数据目录存在
    os.makedirs(app.config["DATA_DIR"], exist_ok=True)
    
    # CORS 配置
    cors_origins = os.environ.get("CORS_ORIGINS", "*")
    if cors_origins == "*":
        CORS(app)
    else:
        CORS(app, origins=cors_origins.split(","))
    
    # 初始化 Swagger
    app.config['SWAGGER'] = {
        'title': '投研问答助手 API',
        'description': '智能投研问答系统 API 文档',
        'version': '1.0.0',
        'uiversion': 3,
        'specs_route': '/docs/'
    }
    Swagger(app)
    
    # 注册蓝图
    app.register_blueprint(agent_bp, url_prefix="/api/v1/agent")
    
    # 健康检查端点
    @app.route("/health")
    def health_check():
        return {"status": "ok", "service": "touyanzhushou-backend"}
    
    return app
