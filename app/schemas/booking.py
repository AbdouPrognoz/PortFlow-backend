from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time
from .common import ResponseBase


class BookingStatusEnum(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    CONSUMED = "CONSUMED"


class BookingBase(BaseModel):
    carrier_user_id: str
    terminal_id: str
    date: date
    start_time: time
    end_time: time


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    carrier_user_id: Optional[str] = None
    driver_user_id: Optional[str] = None
    terminal_id: Optional[str] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[BookingStatusEnum] = None
    decided_by_operator_user_id: Optional[str] = None


class BookingResponse(BookingBase):
    id: str
    driver_user_id: Optional[str] = None
    status: BookingStatusEnum
    decided_by_operator_user_id: Optional[str] = None
    qr_payload: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingListResponse(ResponseBase):
    data: list[BookingResponse]


class BookingConfirmationRequest(BaseModel):
    booking_id: str
    status: BookingStatusEnum
    decided_by_operator_user_id: str