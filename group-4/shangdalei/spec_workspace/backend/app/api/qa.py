"""
问答API
基于 05-用户故事与验收标准.md US-002
基于 09-API接口规格.md
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.database import get_db, get_redis
from app.models import Session as SessionModel, QARecord
from app.schemas import (
    QARequest, QAResponse, QAHistoryResponse, 
    QARecordResponse, ErrorResponse
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/qa", tags=["问答"])

ai_service = AIService()


@router.post("/ask", response_model=QAResponse, responses={
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse}
})
async def ask_question(
    request: QARequest,
    db: Session = Depends(get_db)
):
    """
    提交问答
    AC-002-01: 用户可提交问题并获取回答
    """
    # 验证会话存在
    session = db.query(SessionModel).filter(
        SessionModel.id == request.session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "会话不存在"}
        )
    
    # 调用AI服务获取回答
    answer, answer_source = await ai_service.get_answer(request.query)
    
    # 保存问答记录
    record = QARecord(
        session_id=request.session_id,
        query=request.query,
        answer=answer,
        answer_source=answer_source
    )
    db.add(record)
    db.commit()
    
    # 更新会话时间
    session.updated_at = datetime.utcnow()
    db.commit()
    
    # 缓存到Redis
    redis_client = get_redis()
    if redis_client:
        cache_key = f"qa:recent:{request.session_id}"
        record_data = json.dumps({
            "query": request.query,
            "answer": answer,
            "answer_source": answer_source,
            "created_at": datetime.utcnow().isoformat()
        })
        redis_client.lpush(cache_key, record_data)
        redis_client.ltrim(cache_key, 0, 9)  # 保留最近10条
        redis_client.expire(cache_key, 3600)
    
    return QAResponse(
        answer=answer,
        answer_source=answer_source,
        references=[],
        created_at=record.created_at
    )


@router.get("/history", response_model=QAHistoryResponse)
async def get_history(
    session_id: str = Query(..., description="会话ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    获取问答历史
    AC-002-02: 支持问答历史记录查看
    """
    # 验证会话存在
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "会话不存在"}
        )
    
    # 查询总数
    total = db.query(QARecord).filter(
        QARecord.session_id == session_id
    ).count()
    
    # 分页查询
    offset = (page - 1) * page_size
    records = db.query(QARecord).filter(
        QARecord.session_id == session_id
    ).order_by(QARecord.created_at.desc()).offset(offset).limit(page_size).all()
    
    return QAHistoryResponse(
        records=[
            QARecordResponse(
                query=r.query,
                answer=r.answer,
                answer_source=r.answer_source,
                created_at=r.created_at
            ) for r in records
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/resend/{record_id}", response_model=QAResponse)
async def resend_question(
    record_id: str,
    db: Session = Depends(get_db)
):
    """
    重新发送问题
    AC-002-03: 支持重新发送问题
    """
    # 查找原记录
    record = db.query(QARecord).filter(QARecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": "问答记录不存在"}
        )
    
    # 重新获取回答
    answer, answer_source = await ai_service.get_answer(record.query)
    
    # 保存新记录
    new_record = QARecord(
        session_id=record.session_id,
        query=record.query,
        answer=answer,
        answer_source=answer_source
    )
    db.add(new_record)
    db.commit()
    
    return QAResponse(
        answer=answer,
        answer_source=answer_source,
        references=[],
        created_at=new_record.created_at
    )
