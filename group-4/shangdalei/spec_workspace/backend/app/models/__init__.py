"""
数据模型模块
基于 10-数据模型与存储规格.md
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Session(Base):
    """会话表"""
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=True)
    user_id = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    qa_records = relationship("QARecord", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session {self.id}>"


class QARecord(Base):
    """问答记录表"""
    __tablename__ = "qa_records"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    answer_source = Column(String(50), nullable=False)  # openai, demo, fallback
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # 关系
    session = relationship("Session", back_populates="qa_records")
    
    def __repr__(self):
        return f"<QARecord {self.id}>"
