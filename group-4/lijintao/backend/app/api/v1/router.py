from fastapi import APIRouter
from app.api.v1.endpoints import health, sessions, messages

api_router = APIRouter()

# 健康检查路由（无前缀）
api_router.include_router(health.router, tags=["health"])

# 会话路由
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

# 消息路由（嵌套在 sessions 下）
api_router.include_router(messages.router, prefix="/sessions", tags=["messages"])
