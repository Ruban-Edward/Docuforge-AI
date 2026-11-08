from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.template import DocumentTemplate, TemplateSection, TemplateVersion
from app.schemas.template import (
    TemplateCreate,
    TemplateOut,
    TemplateSectionCreate,
    TemplateSectionOut,
    TemplateSectionUpdate,
    TemplateUpdate,
    TemplateVersionCreate,
    TemplateVersionOut,
    TemplateVersionUpdate,
)

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("", response_model=list[TemplateOut])
async def list_templates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_user),
):
    stmt = select(DocumentTemplate).where(DocumentTemplate.is_active.is_(True))
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(or_(DocumentTemplate.name.ilike(like), DocumentTemplate.code.ilike(like)))
    if category:
        stmt = stmt.where(DocumentTemplate.category == category)
    stmt = stmt.order_by(DocumentTemplate.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [TemplateOut.model_validate(item) for item in items]


@router.post("", response_model=TemplateOut)
async def create_template(
    payload: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    existing = await db.scalar(
        select(DocumentTemplate).where((DocumentTemplate.name == payload.name) | (DocumentTemplate.code == payload.code))
    )
    if existing is not None:
        raise ConflictException(message="Template with this name or code already exists")

    template = DocumentTemplate(**payload.model_dump(), created_by_id=current_user.id)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return TemplateOut.model_validate(template)


@router.get("/{template_id}", response_model=TemplateOut)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_user),
):
    template = await db.get(DocumentTemplate, template_id)
    if template is None:
        raise NotFoundException(message="Template not found")
    return TemplateOut.model_validate(template)


@router.put("/{template_id}", response_model=TemplateOut)
async def update_template(
    template_id: UUID,
    payload: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    template = await db.get(DocumentTemplate, template_id)
    if template is None:
        raise NotFoundException(message="Template not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    await db.commit()
    await db.refresh(template)
    return TemplateOut.model_validate(template)


@router.delete("/{template_id}")
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    template = await db.get(DocumentTemplate, template_id)
    if template is None:
        raise NotFoundException(message="Template not found")
    template.is_active = False
    await db.commit()
    return {"message": "Template deactivated successfully"}


@router.get("/{template_id}/versions", response_model=list[TemplateVersionOut])
async def list_template_versions(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_user),
):
    result = await db.execute(select(TemplateVersion).where(TemplateVersion.template_id == template_id).order_by(TemplateVersion.created_at.desc()))
    items = result.scalars().all()
    return [TemplateVersionOut.model_validate(item) for item in items]


@router.get("/{template_id}/versions/{version_id}", response_model=TemplateVersionOut)
async def get_template_version(
    template_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_user),
):
    version = await db.get(TemplateVersion, version_id)
    if version is None or version.template_id != template_id:
        raise NotFoundException(message="Template version not found")
    return TemplateVersionOut.model_validate(version)


@router.post("/{template_id}/versions", response_model=TemplateVersionOut)
async def create_template_version(
    template_id: UUID,
    payload: TemplateVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    template = await db.get(DocumentTemplate, template_id)
    if template is None:
        raise NotFoundException(message="Template not found")
    existing = await db.scalar(
        select(TemplateVersion).where(
            TemplateVersion.template_id == template_id,
            TemplateVersion.version_number == payload.version_number,
        )
    )
    if existing is not None:
        raise ConflictException(message="A template version with this number already exists")
    version = TemplateVersion(template_id=template_id, created_by_id=current_user.id, **payload.model_dump())
    version.status = "draft"
    version.is_published = False
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return TemplateVersionOut.model_validate(version)


@router.put("/{template_id}/versions/{version_id}", response_model=TemplateVersionOut)
async def update_template_version(
    template_id: UUID,
    version_id: UUID,
    payload: TemplateVersionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    version = await db.get(TemplateVersion, version_id)
    if version is None or version.template_id != template_id:
        raise NotFoundException(message="Template version not found")
    if version.is_published:
        raise ForbiddenException(message="Published template versions are immutable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(version, field, value)
    await db.commit()
    await db.refresh(version)
    return TemplateVersionOut.model_validate(version)


@router.post("/{template_id}/versions/{version_id}/publish")
async def publish_template_version(
    template_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    version = await db.get(TemplateVersion, version_id)
    if version is None or version.template_id != template_id:
        raise NotFoundException(message="Template version not found")
    if version.is_published:
        return {"message": "Template version already published"}
    version.is_published = True
    version.status = "published"
    await db.commit()
    return {"message": "Template version published successfully"}


@router.get("/{template_id}/versions/{version_id}/sections", response_model=list[TemplateSectionOut])
async def list_template_sections(
    template_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(get_current_user),
):
    version = await db.get(TemplateVersion, version_id)
    if version is None or version.template_id != template_id:
        raise NotFoundException(message="Template version not found")
    result = await db.execute(
        select(TemplateSection).where(TemplateSection.template_version_id == version_id).order_by(TemplateSection.order_index.asc())
    )
    items = result.scalars().all()
    return [TemplateSectionOut.model_validate(item) for item in items]


@router.post("/{template_id}/versions/{version_id}/sections", response_model=TemplateSectionOut)
async def create_template_section(
    template_id: UUID,
    version_id: UUID,
    payload: TemplateSectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    version = await db.get(TemplateVersion, version_id)
    if version is None or version.template_id != template_id:
        raise NotFoundException(message="Template version not found")
    if version.is_published:
        raise ForbiddenException(message="Published template versions are immutable")

    existing = await db.scalar(
        select(TemplateSection).where(
            TemplateSection.template_version_id == version_id,
            TemplateSection.section_key == payload.section_key,
        )
    )
    if existing is not None:
        raise ConflictException(message="A section with this key already exists in this template version")

    result = await db.execute(select(TemplateSection).where(TemplateSection.template_version_id == version_id))
    current_count = len(result.scalars().all())
    section = TemplateSection(template_version_id=version_id, **payload.model_dump(), order_index=current_count)
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return TemplateSectionOut.model_validate(section)


@router.put("/{template_id}/versions/{version_id}/sections/{section_id}", response_model=TemplateSectionOut)
async def update_template_section(
    template_id: UUID,
    version_id: UUID,
    section_id: UUID,
    payload: TemplateSectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    version = await db.get(TemplateVersion, version_id)
    if version is None or version.template_id != template_id:
        raise NotFoundException(message="Template version not found")
    if version.is_published:
        raise ForbiddenException(message="Published template versions are immutable")
    section = await db.get(TemplateSection, section_id)
    if section is None or section.template_version_id != version_id:
        raise NotFoundException(message="Template section not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    await db.commit()
    await db.refresh(section)
    return TemplateSectionOut.model_validate(section)


@router.put("/{template_id}/versions/{version_id}/sections/reorder")
async def reorder_template_sections(
    template_id: UUID,
    version_id: UUID,
    section_order: list[UUID] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    version = await db.get(TemplateVersion, version_id)
    if version is None or version.template_id != template_id:
        raise NotFoundException(message="Template version not found")
    if version.is_published:
        raise ForbiddenException(message="Published template versions are immutable")
    if not section_order:
        raise ValidationException(message="Section order cannot be empty")
    sections = await db.execute(select(TemplateSection).where(TemplateSection.template_version_id == version_id, TemplateSection.id.in_(section_order)))
    section_map = {section.id: section for section in sections.scalars().all()}
    if len(section_map) != len(section_order):
        raise NotFoundException(message="One or more template sections were not found")
    for index, section_id in enumerate(section_order):
        section_map[section_id].order_index = index
    await db.commit()
    return {"message": "Template sections reordered successfully"}


@router.delete("/{template_id}/versions/{version_id}/sections/{section_id}")
async def delete_template_section(
    template_id: UUID,
    version_id: UUID,
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    version = await db.get(TemplateVersion, version_id)
    if version is None or version.template_id != template_id:
        raise NotFoundException(message="Template version not found")
    if version.is_published:
        raise ForbiddenException(message="Published template versions are immutable")
    section = await db.get(TemplateSection, section_id)
    if section is None or section.template_version_id != version_id:
        raise NotFoundException(message="Template section not found")
    await db.delete(section)
    await db.commit()
    return {"message": "Template section deleted successfully"}
