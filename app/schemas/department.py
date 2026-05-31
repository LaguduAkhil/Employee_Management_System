"""Department schemas for validation."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class DepartmentCreate(BaseModel):
    """Department creation request."""
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    description: Optional[str] = Field(None, max_length=500)


class DepartmentUpdate(BaseModel):
    """Department update request."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    description: Optional[str] = Field(None, max_length=500)


class DepartmentResponse(BaseModel):
    """Department response."""
    id: int
    name: str
    code: str
    description: Optional[str]
    manager_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        from_attributes = True
