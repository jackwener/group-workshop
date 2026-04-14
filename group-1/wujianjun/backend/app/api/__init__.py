"""
API 蓝图注册
对齐 09-API接口规格：Base URL /api/v1/agent
"""
from flask import Blueprint

agent_bp = Blueprint("agent", __name__)

# 导入路由（在蓝图创建后导入避免循环依赖）
from app.api import routes
