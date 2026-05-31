"""Attendance schemas for validation."""

from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import Optional

from app.core.enums import AttendanceStatusEnum


class AttendanceCreate(BaseModel):
    """Attendance creation request."""
    employee_id: int
    attendance_date: date
    status: AttendanceStatusEnum
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None


class AttendanceUpdate(BaseModel):
    """Attendance update request."""
    status: Optional[AttendanceStatusEnum] = None
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None


class AttendanceResponse(BaseModel):
    """Attendance response."""
    id: int
    employee_id: int
    attendance_date: date
    status: AttendanceStatusEnum
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        from_attributes = True
