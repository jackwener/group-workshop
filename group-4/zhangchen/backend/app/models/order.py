from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id"), nullable=False, index=True)
    order_type = Column(String(10), nullable=False)  # buy, sell
    amount = Column(Numeric(15, 2), nullable=True)  # 买入金额
    shares = Column(Numeric(15, 4), nullable=True)  # 卖出份额
    nav = Column(Numeric(10, 4), nullable=True)  # 成交净值
    status = Column(String(20), default="pending")  # pending, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True), nullable=True)

    # 关系
    user = relationship("User", back_populates="orders")
    contest = relationship("Contest", back_populates="orders")
    fund = relationship("Fund", back_populates="orders")
