from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_roles
from app.models.audit import AuditLog
from app.models.department import Department
from app.models.document import Document
from app.models.template import DocumentTemplate
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    total_users = await db.scalar(select(func.count()).select_from(User))
    total_templates = await db.scalar(select(func.count()).select_from(DocumentTemplate))
    total_documents = await db.scalar(select(func.count()).select_from(Document))
    total_departments = await db.scalar(select(func.count()).select_from(Department))
    return {
        "total_users": total_users or 0,
        "total_templates": total_templates or 0,
        "total_documents": total_documents or 0,
        "total_departments": total_departments or 0,
    }


@router.get("/audit-log")
async def audit_log(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: object = Depends(require_roles("super_admin", "admin")),
):
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit))
    return result.scalars().all()
