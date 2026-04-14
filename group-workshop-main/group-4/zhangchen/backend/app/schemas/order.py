from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class OrderBase(BaseModel):
    order_type: str = Field(..., pattern="^(buy|sell)$")
    fund_id: int


class OrderCreate(OrderBase):
    amount: Optional[Decimal] = Field(None, decimal_places=2, ge=0)  # 买入金额
    shares: Optional[Decimal] = Field(None, decimal_places=4, ge=0)  # 卖出份额


class OrderUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|completed|cancelled)$")


class Order(OrderBase):
    id: int
    user_id: int
    contest_id: int
    amount: Optional[Decimal]
    shares: Optional[Decimal]
    nav: Optional[Decimal]
    status: str
    created_at: datetime
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrderWithFund(Order):
    fund_name: str
    fund_code: str
