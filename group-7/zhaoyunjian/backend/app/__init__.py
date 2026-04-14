import os
from flask import Flask
from flask_cors import CORS
from app.core.config import Config
from app.core.error_handlers import register_error_handlers
from app.core.api_docs import api as swagger_api

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 导入API路由模块（必须在init_app之前导入，以便注册到命名空间）
    from app.api.v1 import agent
    
    # 初始化Swagger API文档（会自动注册路由）
    swagger_api.init_app(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 健康检查端点
    @app.route('/health')
    def health():
        return {'status': 'ok', 'message': 'Service is running'}
    
    return app
