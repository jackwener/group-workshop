"""
Flask 应用工厂
对齐 08-系统架构与技术选型 §2 后端分层结构
"""
from flask import Flask
from flask_cors import CORS
from app.api import agent_bp


def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # CORS 全开放（教学版）
    # 对齐 07-非功能需求 §4 安全需求
    CORS(app)
    
    # 注册蓝图
    # Base URL: /api/v1/agent（对齐 09-API接口规格）
    app.register_blueprint(agent_bp, url_prefix="/api/v1/agent")
    
    return app
