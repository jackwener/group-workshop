import os
from flask import Flask
from flask_cors import CORS
from flask_restx import Api


def create_app():
    app = Flask(__name__)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 配置数据目录
    data_dir = os.environ.get("DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    
    # 初始化 Flask-RESTX API（Swagger文档）
    api = Api(
        app,
        version='1.0',
        title='投研问答助手 API',
        description='投研问答助手后端 API 接口文档',
        doc='/docs',  # Swagger UI 访问路径
        prefix='/api/v1'
    )
    
    # 注册蓝图
    from app.routes.agent_bp import agent_bp
    app.register_blueprint(agent_bp, url_prefix="/api/v1/agent")
    
    # 注册命名空间（用于Swagger文档）
    from app.routes.agent_ns import agent_ns
    api.add_namespace(agent_ns, path='/agent')
    
    @app.route("/health")
    def health_check():
        return {"status": "ok"}
    
    return app
