from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import PrimaryKeyMixin, TimestampMixin


class DocumentTemplate(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_templates"

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    created_by: Mapped["User"] = relationship("User", back_populates="templates")
    versions: Mapped[List["TemplateVersion"]] = relationship(
        "TemplateVersion",
        back_populates="template",
        cascade="all, delete-orphan",
    )
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="template")


class TemplateVersion(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "template_versions"

    template_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("document_templates.id"), nullable=False, index=True)
    version_number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    template: Mapped["DocumentTemplate"] = relationship("DocumentTemplate", back_populates="versions")
    sections: Mapped[List["TemplateSection"]] = relationship(
        "TemplateSection",
        back_populates="template_version",
        cascade="all, delete-orphan",
    )


class TemplateSection(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "template_sections"

    template_version_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("template_versions.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    section_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    section_type: Mapped[str] = mapped_column(String(50), default="text", nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="text", nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    skip_permission: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    not_applicable_permission: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    default_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validation_rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    template_version: Mapped["TemplateVersion"] = relationship("TemplateVersion", back_populates="sections")
