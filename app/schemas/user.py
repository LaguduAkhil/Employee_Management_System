"""User schemas for validation."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.core.enums import RoleEnum


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    """User creation request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: RoleEnum = RoleEnum.EMPLOYEE


class UserResponse(BaseModel):
    """User response - never includes password."""
    id: int
    email: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response after login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # in seconds
    user: UserResponse
