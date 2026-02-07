from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from .common import ResponseBase


class CarrierStatusEnum(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class CarrierProfileBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None  # ISO format date string
    company_name: Optional[str] = None
    proof_document_url: Optional[str] = None


class CarrierProfileCreate(CarrierProfileBase):
    pass


class CarrierProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    company_name: Optional[str] = None
    proof_document_url: Optional[str] = None
    status: Optional[CarrierStatusEnum] = None


class CarrierProfileResponse(CarrierProfileBase):
    user_id: str
    status: CarrierStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarrierListResponse(ResponseBase):
    data: list[CarrierProfileResponse]


class CarrierApprovalRequest(BaseModel):
    carrier_user_id: str
    status: CarrierStatusEnum
    reason: Optional[str] = None