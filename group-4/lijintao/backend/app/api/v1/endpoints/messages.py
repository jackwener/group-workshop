import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.message_service import MessageService
from app.schemas.common import BaseResponse
from app.schemas.message import MessageResponse, MessageListResponse

router = APIRouter()


@router.get("/{session_id}/messages", response_model=BaseResponse[MessageListResponse])
async def list_messages(
    session_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db)
):
    """获取会话消息列表"""
    service = MessageService(db)
    
    try:
        messages, total = service.get_by_session(session_id, page, page_size)
    except Exception as e:
        if "不存在" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise
    
    # 转换为响应格式
    message_responses = [
        MessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            tokens=m.tokens,
            model=m.model,
            provider=m.provider,
            latency_ms=m.latency_ms,
            created_at=m.created_at
        )
        for m in messages
    ]
    
    return BaseResponse(
        traceId=str(uuid.uuid4()),
        data=MessageListResponse(
            messages=message_responses,
            total=total,
            page=page,
            page_size=page_size
        ),
        timestamp=datetime.utcnow()
    )
