from typing import Tuple, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.session import Session as SessionModel
from app.models.message import Message as MessageModel
from app.core.exceptions import NotFoundException


class SessionService:
    """会话业务逻辑服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, title: str = "新会话") -> SessionModel:
        """创建会话
        
        Args:
            user_id: 用户ID
            title: 会话标题
            
        Returns:
            创建的会话对象
        """
        session = SessionModel(
            user_id=user_id,
            title=title,
            is_active=True
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_by_id(self, session_id: int) -> SessionModel | None:
        """获取单个会话，包含 message_count
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话对象或 None
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id,
            SessionModel.is_active == True
        ).first()
        
        if session:
            # 计算 message_count
            message_count = self.db.query(func.count(MessageModel.id)).filter(
                MessageModel.session_id == session_id
            ).scalar() or 0
            session.message_count = message_count
        
        return session
    
    def get_list(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[List[SessionModel], int]:
        """分页获取用户会话列表，按 updated_at DESC 排序
        
        Args:
            user_id: 用户ID
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            (sessions, total) 元组
        """
        query = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True
        ).order_by(SessionModel.updated_at.desc())
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        sessions = query.offset(offset).limit(page_size).all()
        
        # 为每个会话添加 message_count
        for session in sessions:
            message_count = self.db.query(func.count(MessageModel.id)).filter(
                MessageModel.session_id == session.id
            ).scalar() or 0
            session.message_count = message_count
        
        return sessions, total
    
    def delete(self, session_id: int) -> dict:
        """删除会话（级联删除消息）
        
        Args:
            session_id: 会话ID
            
        Returns:
            包含删除信息的字典
            
        Raises:
            NotFoundException: 会话不存在
        """
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        
        if not session:
            raise NotFoundException(message=f"会话 {session_id} 不存在")
        
        # 统计消息数量（在删除前）
        messages_count = self.db.query(func.count(MessageModel.id)).filter(
            MessageModel.session_id == session_id
        ).scalar() or 0
        
        # 删除会话（级联删除消息由数据库外键约束处理）
        self.db.delete(session)
        self.db.commit()
        
        return {
            "id": session_id,
            "deleted": True,
            "deleted_messages_count": messages_count
        }
