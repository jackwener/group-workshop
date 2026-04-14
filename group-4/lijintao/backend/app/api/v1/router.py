from fastapi import APIRouter
from app.api.v1.endpoints import health, sessions, messages, chat

api_router = APIRouter()

# 健康检查路由（无前缀）
api_router.include_router(health.router, tags=["health"])

# 会话路由
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

# 消息路由（嵌套在 sessions 下）- GET 方法
api_router.include_router(messages.router, prefix="/sessions", tags=["messages"])

# 聊天路由（嵌套在 sessions 下）- POST 方法
api_router.include_router(chat.router, prefix="/sessions", tags=["chat"])
