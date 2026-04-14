from sqlalchemy import Column, Integer, String, Numeric, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Fund(Base):
    __tablename__ = "funds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=True)  # 股票型、债券型、混合型、货币型、指数型
    company = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    risk_level = Column(Integer, nullable=True)  # 1-5级
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    prices = relationship("FundPrice", back_populates="fund", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="fund")
    holdings = relationship("Holding", back_populates="fund")
    transactions = relationship("Transaction", back_populates="fund")


class FundPrice(Base):
    __tablename__ = "fund_prices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey("funds.id"), nullable=False, index=True)
    nav = Column(Numeric(10, 4), nullable=False)  # 单位净值
    accum_nav = Column(Numeric(10, 4), nullable=True)  # 累计净值
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    fund = relationship("Fund", back_populates="prices")

    __table_args__ = (
        # 确保每个基金每天只有一条记录
        {"sqlite_autoincrement": True},
    )
