from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import ROLE_PERMISSIONS, RoleEnum
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User


async def seed_system_roles(db: AsyncSession) -> None:
    for name, permissions in ROLE_PERMISSIONS.items():
        role = await db.scalar(select(Role).where(Role.name == name))
        if role is None:
            role = Role(
                name=name,
                display_name=name.replace("_", " ").title(),
                description=f"System role for {name}",
                permissions=list(permissions),
                is_system_role=True,
            )
            db.add(role)
    await db.commit()


async def seed_default_admin(db: AsyncSession) -> None:
    admin_user = await db.scalar(select(User).where(User.email == settings.INITIAL_ADMIN_EMAIL))
    if admin_user is not None:
        return
    super_admin_role = await db.scalar(select(Role).where(Role.name == RoleEnum.SUPER_ADMIN.value))
    if super_admin_role is None:
        await seed_system_roles(db)
        super_admin_role = await db.scalar(select(Role).where(Role.name == RoleEnum.SUPER_ADMIN.value))
    user = User(
        email=settings.INITIAL_ADMIN_EMAIL,
        username=settings.INITIAL_ADMIN_USERNAME,
        hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
        full_name=settings.INITIAL_ADMIN_FULL_NAME,
        role_id=super_admin_role.id,
        is_active=True,
        is_verified=True,
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
