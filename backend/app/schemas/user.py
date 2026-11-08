from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_name: str = "developer"
    department_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=100)
    full_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
    role_name: Optional[str] = None
    is_active: Optional[bool] = None


class RoleAssignment(BaseModel):
    role_name: str


class UserOut(UserBase):
    id: UUID
    role_name: str
    department_id: Optional[UUID] = None
    is_active: bool
    is_verified: bool
    model_config = ConfigDict(from_attributes=True)

