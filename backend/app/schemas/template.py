from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TemplateBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    code: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    code: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateOut(TemplateBase):
    id: UUID
    is_active: bool
    model_config = ConfigDict(from_attributes=True)



class TemplateVersionBase(BaseModel):
    version_number: str = Field(..., min_length=1)
    notes: Optional[str] = None


class TemplateVersionCreate(TemplateVersionBase):
    pass


class TemplateVersionUpdate(BaseModel):
    version_number: Optional[str] = Field(default=None, min_length=1)
    status: Optional[str] = None
    notes: Optional[str] = None
    file_url: Optional[str] = None


class TemplateVersionOut(TemplateVersionBase):
    id: UUID
    status: str
    is_published: bool
    template_id: UUID
    model_config = ConfigDict(from_attributes=True)



class TemplateSectionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    section_key: str = Field(..., min_length=1, max_length=100)
    section_type: str = "text"
    content_type: str = "text"
    content: Optional[str] = None
    status: str = "active"
    is_required: bool = False
    skip_permission: Optional[str] = None
    not_applicable_permission: Optional[str] = None
    default_value: Optional[str] = None
    validation_rules: Optional[str] = None


class TemplateSectionCreate(TemplateSectionBase):
    pass


class TemplateSectionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    section_key: Optional[str] = Field(default=None, min_length=1, max_length=100)
    section_type: Optional[str] = None
    content_type: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    is_required: Optional[bool] = None
    skip_permission: Optional[str] = None
    not_applicable_permission: Optional[str] = None
    default_value: Optional[str] = None
    validation_rules: Optional[str] = None


class TemplateSectionOut(TemplateSectionBase):
    id: UUID
    order_index: int
    template_version_id: UUID
    model_config = ConfigDict(from_attributes=True)

