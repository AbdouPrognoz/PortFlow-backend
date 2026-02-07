from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .common import ResponseBase


class DriverStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class DriverProfileBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None  # ISO format date string
    truck_number: Optional[str] = None
    truck_plate: Optional[str] = None
    driving_license_url: Optional[str] = None
    carrier_user_id: str


class DriverProfileCreate(DriverProfileBase):
    pass


class DriverProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    truck_number: Optional[str] = None
    truck_plate: Optional[str] = None
    driving_license_url: Optional[str] = None
    carrier_user_id: Optional[str] = None
    status: Optional[DriverStatusEnum] = None


class DriverProfileResponse(DriverProfileBase):
    user_id: str
    status: DriverStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DriverListResponse(ResponseBase):
    data: list[DriverProfileResponse]