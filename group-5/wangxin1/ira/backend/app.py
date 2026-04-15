"""
Flask 应用入口
"""
import os
import json
from pathlib import Path
from flask import Flask, redirect, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取静态文件目录
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / 'static'


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__, static_folder=str(STATIC_DIR))
    
    # 配置 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    from blueprints.agent_bp import agent_bp
    app.register_blueprint(agent_bp)
    
    @app.route('/')
    def index():
        return redirect('/apidocs')
    
    @app.route('/api')
    def api_info():
        return {
            "name": "投研问答助手 (IRA)",
            "version": "1.0.0",
            "docs": "/apidocs",
            "health": "/api/v1/agent/health"
        }
    
    @app.route('/apidocs')
    @app.route('/apidocs/')
    def swagger_ui():
        """Swagger UI 页面"""
        return send_from_directory(str(STATIC_DIR), 'swagger-ui.html')
    
    @app.route('/swagger.json')
    def swagger_json():
        """Swagger JSON 规范"""
        return send_from_directory(str(STATIC_DIR), 'swagger.json')
    
    return app


# 创建应用实例
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
