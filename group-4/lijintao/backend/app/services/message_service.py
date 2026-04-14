from typing import Tuple, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.message import Message as MessageModel
from app.models.session import Session as SessionModel
from app.core.exceptions import NotFoundException


class MessageService:
    """消息业务逻辑服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_session(
        self, 
        session_id: int, 
        page: int = 1, 
        page_size: int = 50
    ) -> Tuple[List[MessageModel], int]:
        """分页获取会话消息，按 created_at ASC 排序
        
        Args:
            session_id: 会话ID
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            (messages, total) 元组
        """
        # 检查会话是否存在
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if not session:
            raise NotFoundException(message=f"会话 {session_id} 不存在")
        
        query = self.db.query(MessageModel).filter(
            MessageModel.session_id == session_id
        ).order_by(MessageModel.created_at.asc())
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        messages = query.offset(offset).limit(page_size).all()
        
        return messages, total
    
    def create(
        self, 
        session_id: int, 
        role: str, 
        content: str, 
        **kwargs
    ) -> MessageModel:
        """创建消息，同时更新 session 的 updated_at
        
        Args:
            session_id: 会话ID
            role: 角色 (user/assistant)
            content: 消息内容
            **kwargs: 其他字段 (tokens, model, provider, latency_ms, metadata_)
            
        Returns:
            创建的消息对象
            
        Raises:
            NotFoundException: 会话不存在
        """
        # 检查会话是否存在
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if not session:
            raise NotFoundException(message=f"会话 {session_id} 不存在")
        
        # 创建消息
        message = MessageModel(
            session_id=session_id,
            role=role,
            content=content,
            tokens=kwargs.get("tokens"),
            model=kwargs.get("model"),
            provider=kwargs.get("provider"),
            latency_ms=kwargs.get("latency_ms"),
            metadata_=kwargs.get("metadata_", {}),
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        
        # 更新会话的 updated_at
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
