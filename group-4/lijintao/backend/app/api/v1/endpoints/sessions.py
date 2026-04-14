import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.session_service import SessionService
from app.schemas.common import BaseResponse
from app.schemas.session import SessionCreate, SessionResponse, SessionListResponse
from app.core.exceptions import NotFoundException

router = APIRouter()

# MVP 阶段硬编码用户 ID
DEFAULT_USER_ID = 1


@router.get("", response_model=BaseResponse[SessionListResponse])
async def list_sessions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取会话列表"""
    service = SessionService(db)
    sessions, total = service.get_list(DEFAULT_USER_ID, page, page_size)
    
    # 转换为响应格式
    session_responses = [
        SessionResponse(
            id=s.id,
            title=s.title,
            message_count=getattr(s, 'message_count', 0),
            is_active=s.is_active,
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        for s in sessions
    ]
    
    return BaseResponse(
        traceId=str(uuid.uuid4()),
        data=SessionListResponse(
            sessions=session_responses,
            total=total,
            page=page,
            page_size=page_size
        ),
        timestamp=datetime.utcnow()
    )


@router.post("", response_model=BaseResponse[SessionResponse])
async def create_session(
    body: SessionCreate,
    db: Session = Depends(get_db)
):
    """创建会话"""
    service = SessionService(db)
    session = service.create(DEFAULT_USER_ID, body.title)
    
    return BaseResponse(
        traceId=str(uuid.uuid4()),
        data=SessionResponse(
            id=session.id,
            title=session.title,
            message_count=0,
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at
        ),
        timestamp=datetime.utcnow()
    )


@router.get("/{session_id}", response_model=BaseResponse[SessionResponse])
async def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """获取会话详情"""
    service = SessionService(db)
    session = service.get_by_id(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    return BaseResponse(
        traceId=str(uuid.uuid4()),
        data=SessionResponse(
            id=session.id,
            title=session.title,
            message_count=getattr(session, 'message_count', 0),
            is_active=session.is_active,
            created_at=session.created_at,
            updated_at=session.updated_at
        ),
        timestamp=datetime.utcnow()
    )


@router.delete("/{session_id}", response_model=BaseResponse[dict])
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """删除会话"""
    service = SessionService(db)
    result = service.delete(session_id)
    
    return BaseResponse(
        traceId=str(uuid.uuid4()),
        data=result,
        timestamp=datetime.utcnow()
    )
