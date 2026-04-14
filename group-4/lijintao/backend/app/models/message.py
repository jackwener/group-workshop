from datetime import datetime
from typing import Any
from sqlalchemy import String, Text, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Message(Base):
    """消息模型"""
    
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    model: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False
    )
    
    # 关系定义
    session: Mapped["Session"] = relationship("Session", back_populates="messages")
    
    # 显式定义索引
    __table_args__ = (
        Index("idx_messages_session_id", "session_id"),
        Index("idx_messages_created_at", "created_at"),
    )
