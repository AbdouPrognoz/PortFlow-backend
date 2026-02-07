from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
from .common import ResponseBase


class UserRoleEnum(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    CARRIER = "CARRIER"
    DRIVER = "DRIVER"


class UserBase(BaseModel):
    email: EmailStr
    role: UserRoleEnum
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserProfile(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None  # ISO format date string


class OperatorProfile(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    terminal_id: Optional[str] = None


class CarrierProfile(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    company_name: Optional[str] = None
    status: str = "PENDING"  # Default status for new registrations


class DriverProfile(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    truck_number: Optional[str] = None
    truck_plate: Optional[str] = None
    carrier_user_id: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    # Profile information depending on role
    profile: Optional[dict] = None

    class Config:
        from_attributes = True


class UserListResponse(ResponseBase):
    data: list[UserResponse]