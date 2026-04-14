from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class ContestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    initial_balance: Decimal = Field(default=100000.00, decimal_places=2)
    start_date: datetime
    end_date: datetime
    rules: Optional[str] = None


class ContestCreate(ContestBase):
    pass


class ContestUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    rules: Optional[str] = None


class Contest(ContestBase):
    id: int
    status: str
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ContestParticipantBase(BaseModel):
    current_balance: Decimal = Field(..., decimal_places=2)
    total_assets: Decimal = Field(..., decimal_places=2)


class ContestParticipantCreate(BaseModel):
    contest_id: int


class ContestParticipant(ContestParticipantBase):
    id: int
    contest_id: int
    user_id: int
    total_return: Decimal
    rank: Optional[int]
    joined_at: datetime

    class Config:
        from_attributes = True


class ContestParticipantWithUser(ContestParticipant):
    username: str
    nickname: Optional[str]


class ContestDetail(Contest):
    participant_count: int = 0
    is_participating: bool = False
    my_rank: Optional[int] = None
