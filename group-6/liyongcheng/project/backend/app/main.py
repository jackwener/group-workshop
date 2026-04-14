"""Flask 应用主入口"""
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from app.config import config
from app.routes import research_bp


def create_app() -> Flask:
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    app.config['JSON_AS_ASCII'] = False  # 支持中文JSON
    
    # Swagger配置
    app.config['SWAGGER'] = {
        'title': '研报阅读系统 API',
        'description': '研报解析、对比与股价查询服务',
        'version': '1.0.0',
        'uiversion': 3,
        'specs_route': '/api/docs/',
    }
    
    # 初始化Swagger
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "研报阅读系统 API",
            "description": "研报解析、对比与股价查询服务",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@example.com"
            }
        },
        "basePath": "/api/v1/research",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        },
        "tags": [
            {"name": "研报管理", "description": "研报上传、查询、删除等操作"},
            {"name": "研报对比", "description": "多份研报横向对比分析"},
            {"name": "股价查询", "description": "股票实时价格查询"},
            {"name": "系统", "description": "系统健康检查等"}
        ]
    }
    Swagger(app, template=swagger_template)
    
    # 初始化数据目录
    config.init_app()
    
    # 配置CORS
    CORS(app, origins='*')  # 开发环境全开放
    
    # 注册蓝图
    app.register_blueprint(research_bp)
    
    # API根路径 - 重定向到Swagger文档
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'service': '研报阅读系统 API',
            'version': '1.0.0',
            'docs': '/api/docs/',
            'health': '/health'
        })
    
    # 健康检查端点
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'service': 'research-system'}
    
    return app


# 创建应用实例
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
