"""Employee schemas for validation."""

from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

from app.core.enums import EmployeeStatusEnum


class EmployeeCreate(BaseModel):
    """Employee creation request."""
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    department_id: int
    employee_code: str = Field(..., min_length=2, max_length=20)
    date_of_birth: Optional[date] = None
    date_of_joining: Optional[date] = None
    password: str = Field(..., min_length=8)


class EmployeeUpdate(BaseModel):
    """Employee update request."""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = None
    date_of_joining: Optional[date] = None
    employment_status: Optional[EmployeeStatusEnum] = None
    casual_leaves: Optional[int] = None
    sick_leaves: Optional[int] = None
    earned_leaves: Optional[int] = None


class EmployeeResponse(BaseModel):
    """Employee response."""
    id: int
    user_id: int
    employee_code: str
    first_name: str
    last_name: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    date_of_joining: Optional[date]
    department_id: int
    employment_status: EmployeeStatusEnum
    casual_leaves: int
    sick_leaves: int
    earned_leaves: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Employee list response with pagination."""
    total: int
    page: int
    page_size: int
    data: list[EmployeeResponse]
