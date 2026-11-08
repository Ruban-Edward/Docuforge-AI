from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    code: Optional[str] = Field(default=None, min_length=2, max_length=50)
    description: Optional[str] = None
    parent_department_id: Optional[UUID] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    code: Optional[str] = Field(default=None, min_length=2, max_length=50)
    description: Optional[str] = None
    parent_department_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class DepartmentOut(DepartmentBase):
    id: UUID
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

