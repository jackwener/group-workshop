"""
会话管理API
基于 05-用户故事与验收标准.md US-001
基于 09-API接口规格.md
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import json

from app.database import get_db, get_redis
from app.models import Session as SessionModel
from app.schemas import (
    SessionCreate, SessionResponse, SessionListResponse, 
    SuccessResponse, ErrorResponse
)
from app.config import settings

router = APIRouter(prefix="/api/sessions", tags=["会话管理"])

# 默认用户ID（演示用）
DEFAULT_USER_ID = "default-user"


@router.post("", response_model=SessionResponse, responses={
    400: {"model": ErrorResponse}
})
async def create_session(
    request: SessionCreate,
    db: Session = Depends(get_db)
):
    """
    创建会话
    AC-001-01: 用户可创建新会话
    """
    # 检查会话数量上限
    count = db.query(SessionModel).filter(
        SessionModel.user_id == DEFAULT_USER_ID
    ).count()
    
    if count >= settings.MAX_SESSIONS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail={"error": "VALIDATION_ERROR", "message": "会话数量已达上限"}
        )
    
    # 创建会话
    session = SessionModel(
        user_id=DEFAULT_USER_ID,
        name=request.name or f"会话 {count + 1}"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # 缓存到Redis
    redis_client = get_redis()
    if redis_client:
        cache_key = f"session:{session.id}"
        redis_client.hset(
            cache_key,
            mapping={
                "name": session.name or "",
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat()
            }
        )
        redis_client.expire(cache_key, settings.SESSION_CACHE_TTL)
    
    return SessionResponse(
        session_id=session.id,
        name=session.name,
        created_at=session.created_at
    )


@router.get("", response_model=SessionListResponse)
async def list_sessions(db: Session = Depends(get_db)):
    """
    获取会话列表
    AC-001-03: 用户可切换不同会话
    """
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == DEFAULT_USER_ID
    ).order_by(SessionModel.updated_at.desc()).all()
    
    return SessionListResponse(
        sessions=[
            SessionResponse(
                session_id=s.id,
                name=s.name,
                created_at=s.created_at,
                updated_at=s.updated_at
            ) for s in sessions
        ],
        total=len(sessions)
    )


@router.delete("/{session_id}", response_model=SuccessResponse, responses={
    404: {"model": ErrorResponse}
})
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    删除会话
    AC-001-02: 用户可删除会话
    """
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == DEFAULT_USER_ID
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "会话不存在"}
        )
    
    db.delete(session)
    db.commit()
    
    # 清除Redis缓存
    redis_client = get_redis()
    if redis_client:
        redis_client.delete(f"session:{session_id}")
        redis_client.delete(f"qa:recent:{session_id}")
    
    return SuccessResponse()
