from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    transaction_type: str = Field(..., pattern="^(buy|sell)$")
    fund_id: int
    shares: Decimal = Field(..., decimal_places=4, gt=0)
    nav: Decimal = Field(..., decimal_places=4, gt=0)
    amount: Decimal = Field(..., decimal_places=2, gt=0)
    fee: Decimal = Field(default=0, decimal_places=2, ge=0)


class TransactionCreate(TransactionBase):
    contest_id: int


class Transaction(TransactionBase):
    id: int
    user_id: int
    contest_id: int
    transaction_date: datetime

    class Config:
        from_attributes = True


class TransactionWithFund(Transaction):
    fund_name: str
    fund_code: str


class TransactionSummary(BaseModel):
    total_buy: Decimal
    total_sell: Decimal
    total_fee: Decimal
    transaction_count: int
