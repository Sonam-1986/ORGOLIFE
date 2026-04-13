"""
Shared Pydantic base models and response envelopes.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class PyObjectId(str):
    """String representation of MongoDB ObjectId for Pydantic v2."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        from bson import ObjectId
        if isinstance(v, str):
            return str(v)
        return str(v)


class BaseResponse(BaseModel):
    """Standard success envelope."""
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error envelope."""
    success: bool = False
    message: str
    detail: Optional[Any] = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    """Paginated list envelope."""
    success: bool = True
    items: List[Any]
    pagination: PaginationMeta


class AddressSchema(BaseModel):
    state: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    full_address: str = Field(..., min_length=5, max_length=500)
