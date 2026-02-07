from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List
from enum import Enum


T = TypeVar('T')


class ResponseStatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ResponseBase(BaseModel):
    status: ResponseStatusEnum
    message: str
    data: Optional[T] = None


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel):
    data: List[T]
    total: int
    skip: int
    limit: int