"""Leave schemas for validation."""

from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import Optional

from app.core.enums import LeaveStatusEnum, LeaveTypeEnum


class LeaveCreate(BaseModel):
    """Leave creation request."""
    leave_type: LeaveTypeEnum
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=10, max_length=1000)
    number_of_days: float = Field(..., gt=0)


class LeaveUpdate(BaseModel):
    """Leave update request."""
    status: Optional[LeaveStatusEnum] = None
    remarks: Optional[str] = Field(None, max_length=500)


class LeaveResponse(BaseModel):
    """Leave response."""
    id: int
    employee_id: int
    leave_type: LeaveTypeEnum
    start_date: date
    end_date: date
    reason: str
    number_of_days: float
    status: LeaveStatusEnum
    remarks: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveListResponse(BaseModel):
    """Leave list response with pagination."""
    total: int
    page: int
    page_size: int
    data: list[LeaveResponse]
