from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime
from .user import UserResponse


class UserRoleEnum(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    CARRIER = "CARRIER"
    DRIVER = "DRIVER"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRoleEnum
    first_name: str
    last_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None  # ISO format date string (YYYY-MM-DD)
    company_name: Optional[str] = None  # For carriers only
    carrier_user_id: Optional[str] = None  # For drivers only - UUID of the carrier


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse