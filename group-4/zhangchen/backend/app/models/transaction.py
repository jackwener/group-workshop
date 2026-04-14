from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id"), nullable=False, index=True)
    transaction_type = Column(String(10), nullable=False)  # buy, sell
    shares = Column(Numeric(15, 4), nullable=False)
    nav = Column(Numeric(10, 4), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    fee = Column(Numeric(10, 2), default=0)  # 手续费
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User", back_populates="transactions")
    contest = relationship("Contest", back_populates="transactions")
    fund = relationship("Fund", back_populates="transactions")
