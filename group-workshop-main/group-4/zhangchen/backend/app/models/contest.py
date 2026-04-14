from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    initial_balance = Column(Numeric(15, 2), default=100000.00)  # 初始资金
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="pending")  # pending, active, ended
    rules = Column(Text, nullable=True)  # JSON格式存储规则
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    creator = relationship("User", back_populates="created_contests")
    participants = relationship("ContestParticipant", back_populates="contest", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="contest")
    holdings = relationship("Holding", back_populates="contest")
    transactions = relationship("Transaction", back_populates="contest")


class ContestParticipant(Base):
    __tablename__ = "contest_participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    current_balance = Column(Numeric(15, 2), nullable=False)  # 当前现金余额
    total_assets = Column(Numeric(15, 2), nullable=False)  # 总资产
    total_return = Column(Numeric(10, 4), default=0)  # 总收益率
    rank = Column(Integer, nullable=True)  # 当前排名
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    contest = relationship("Contest", back_populates="participants")
    user = relationship("User", back_populates="contest_participants")

    __table_args__ = (
        UniqueConstraint('contest_id', 'user_id', name='uix_contest_user'),
    )
