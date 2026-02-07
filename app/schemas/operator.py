from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .common import ResponseBase


class OperatorProfileBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None  # ISO format date string
    terminal_id: Optional[str] = None


class OperatorProfileCreate(OperatorProfileBase):
    pass


class OperatorProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    terminal_id: Optional[str] = None


class OperatorProfileResponse(OperatorProfileBase):
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OperatorListResponse(ResponseBase):
    data: list[OperatorProfileResponse]