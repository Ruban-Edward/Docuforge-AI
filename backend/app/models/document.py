from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import PrimaryKeyMixin, TimestampMixin


class Document(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(100), default="general", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    source_file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("document_templates.id"), nullable=True, index=True)
    template_version_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("template_versions.id"), nullable=True, index=True)
    created_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    department_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True, index=True)
    review_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    template: Mapped[Optional["DocumentTemplate"]] = relationship("DocumentTemplate", back_populates="documents")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="documents")
    created_by: Mapped["User"] = relationship("User", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    sections: Mapped[List["DocumentSection"]] = relationship(
        "DocumentSection",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    processing_jobs: Mapped[List["AIProcessingJob"]] = relationship(
        "AIProcessingJob",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    review_records: Mapped[List["ReviewRecord"]] = relationship("ReviewRecord", back_populates="document")


class DocumentVersion(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_versions"

    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="versions")


class DocumentSection(Base, PrimaryKeyMixin, TimestampMixin):
    __tablename__ = "document_sections"

    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    section_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    content_source: Mapped[str] = mapped_column(String(50), default="user_provided", nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="sections")
