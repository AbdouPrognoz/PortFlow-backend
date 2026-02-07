from pydantic import BaseModel, field_serializer
from typing import Optional, Any
from datetime import datetime
from enum import Enum
from uuid import UUID
from .common import ResponseBase


class TerminalStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


class TerminalBase(BaseModel):
    name: str
    max_slots: int
    available_slots: int
    coord_x: float
    coord_y: float


class TerminalCreate(TerminalBase):
    pass


class TerminalUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[TerminalStatusEnum] = None
    max_slots: Optional[int] = None
    available_slots: Optional[int] = None
    coord_x: Optional[float] = None
    coord_y: Optional[float] = None


class TerminalResponse(TerminalBase):
    id: Any  # UUID or str
    status: TerminalStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @field_serializer('id')
    def serialize_id(self, id: Any) -> str:
        return str(id) if id else None


class TerminalListResponse(ResponseBase):
    data: list[TerminalResponse]