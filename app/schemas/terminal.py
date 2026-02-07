from pydantic import BaseModel
from typing import Optional
from datetime import datetime
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
    id: str
    status: TerminalStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TerminalListResponse(ResponseBase):
    data: list[TerminalResponse]