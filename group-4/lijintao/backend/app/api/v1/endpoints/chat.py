import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import BaseResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{session_id}/messages", response_model=None)
async def send_message(
    session_id: int, 
    request: ChatRequest, 
    db: Session = Depends(get_db)
):
    """发送消息并获取回复
    
    - stream=true: 返回 SSE 流式响应
    - stream=false: 返回 JSON 响应
    """
    chat_service = ChatService(db)
    
    if request.stream:
        # 流式响应
        async def event_generator():
            async for event in chat_service.chat(
                session_id, 
                request.content, 
                stream=True,
                model=request.model
            ):
                yield event
        
        return EventSourceResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    else:
        # 非流式响应
        try:
            result = await chat_service.chat(
                session_id, 
                request.content, 
                stream=False,
                model=request.model
            )
            return BaseResponse(
                traceId=str(uuid.uuid4()),
                data=result,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
