from pydantic import BaseModel, field_serializer
from typing import Optional, Any
from datetime import datetime, date, time
from enum import Enum
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


class BookingResponse(BaseModel):
    id: Any
    carrier_user_id: Any
    terminal_id: Any
    date: date
    start_time: time
    end_time: time
    driver_user_id: Optional[Any] = None
    status: BookingStatusEnum
    decided_by_operator_user_id: Optional[Any] = None
    qr_payload: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @field_serializer('id', 'carrier_user_id', 'terminal_id', 'driver_user_id', 'decided_by_operator_user_id')
    def serialize_uuid(self, value: Any) -> Optional[str]:
        return str(value) if value else None


class BookingListResponse(ResponseBase):
    data: list[BookingResponse]


class BookingConfirmationRequest(BaseModel):
    booking_id: str
    status: BookingStatusEnum
    decided_by_operator_user_id: str