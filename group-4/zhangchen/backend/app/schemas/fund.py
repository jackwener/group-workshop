from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


class FundBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    type: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    risk_level: Optional[int] = Field(None, ge=1, le=5)


class FundCreate(FundBase):
    pass


class Fund(FundBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FundPriceBase(BaseModel):
    nav: Decimal = Field(..., decimal_places=4)
    accum_nav: Optional[Decimal] = Field(None, decimal_places=4)
    date: date


class FundPriceCreate(FundPriceBase):
    fund_id: int


class FundPrice(FundPriceBase):
    id: int
    fund_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FundWithPrice(Fund):
    latest_nav: Optional[Decimal] = None
    latest_date: Optional[date] = None
    daily_change: Optional[Decimal] = None
    daily_change_rate: Optional[Decimal] = None


class FundChartData(BaseModel):
    dates: List[str]
    navs: List[float]
    accum_navs: List[float]
