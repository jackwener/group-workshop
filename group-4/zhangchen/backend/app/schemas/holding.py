from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class HoldingBase(BaseModel):
    fund_id: int
    shares: Decimal = Field(..., decimal_places=4, ge=0)


class HoldingCreate(HoldingBase):
    contest_id: int
    avg_cost: Decimal = Field(..., decimal_places=4)


class Holding(HoldingBase):
    id: int
    user_id: int
    contest_id: int
    avg_cost: Decimal
    current_nav: Optional[Decimal]
    market_value: Optional[Decimal]
    profit_loss: Optional[Decimal]
    return_rate: Optional[Decimal]
    updated_at: datetime

    class Config:
        from_attributes = True


class HoldingWithFund(Holding):
    fund_name: str
    fund_code: str
    fund_type: Optional[str]
