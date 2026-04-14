import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv

load_dotenv()

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "M4-RA 研报聚合分析助手 API",
        "version": "1.0",
        "description": "M4-RA 研报聚合分析助手 Flask 后端接口文档，覆盖能力查询、会话管理、智能问答与研报管理能力。"
    },
    "basePath": "/api/v1/agent",
    "schemes": ["http"],
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}


def create_app(data_dir=None):
    app = Flask(__name__)
    CORS(app)
    Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    
    if data_dir:
        app.config['DATA_DIR'] = data_dir
    else:
        app.config['DATA_DIR'] = os.path.join(os.path.dirname(__file__), 'data')
    
    # 确保数据目录存在
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    from agent_bp import agent_bp
    app.register_blueprint(agent_bp, url_prefix='/api/v1/agent')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
