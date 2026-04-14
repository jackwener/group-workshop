from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id"), nullable=False, index=True)
    shares = Column(Numeric(15, 4), nullable=False, default=0)  # 持有份额
    avg_cost = Column(Numeric(10, 4), nullable=False, default=0)  # 平均成本
    current_nav = Column(Numeric(10, 4), nullable=True)  # 当前净值
    market_value = Column(Numeric(15, 2), nullable=True)  # 市值
    profit_loss = Column(Numeric(15, 2), nullable=True)  # 盈亏金额
    return_rate = Column(Numeric(10, 4), nullable=True)  # 收益率
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="holdings")
    contest = relationship("Contest", back_populates="holdings")
    fund = relationship("Fund", back_populates="holdings")

    __table_args__ = (
        UniqueConstraint('user_id', 'contest_id', 'fund_id', name='uix_user_contest_fund'),
    )
