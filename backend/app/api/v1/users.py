from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.role import Role
from app.models.user import User
from app.schemas.user import RoleAssignment, UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


async def user_to_out(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "role_name": user.role.name if user.role else "developer",
        "department_id": user.department_id,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }


async def ensure_admin_protection(db: AsyncSession, user: User) -> None:
    if user.role is None or user.role.name not in {"admin", "super_admin"}:
        return
    active_admins = await db.scalar(
        select(User.id).join(Role).where(
            User.deleted_at.is_(None),
            User.is_active.is_(True),
            Role.name.in_(["admin", "super_admin"]),
            User.id != user.id,
        )
    )
    if active_admins is None:
        raise ForbiddenException(message="Cannot deactivate or remove the last active administrator")


@router.get("", response_model=list[UserOut])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    role_name: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin", "manager")),
) -> list[dict[str, Any]]:
    stmt = select(User).options(selectinload(User.role)).where(User.deleted_at.is_(None))
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(or_(User.email.ilike(like), User.username.ilike(like), User.full_name.ilike(like)))
    if role_name:
        stmt = stmt.join(Role).where(Role.name == role_name)
    if is_active is not None:
        stmt = stmt.where(User.is_active.is_(is_active))
    stmt = stmt.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [await user_to_out(user) for user in users]


@router.post("", response_model=UserOut)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin")),
) -> dict[str, Any]:
    role = await db.scalar(select(Role).where(Role.name == payload.role_name))
    if role is None:
        raise NotFoundException(message=f"Role '{payload.role_name}' not found")
    existing = await db.scalar(select(User).where(or_(User.email == payload.email, User.username == payload.username)))
    if existing is not None:
        raise ConflictException(message="A user with that email or username already exists")
    user = User(
        email=str(payload.email),
        username=payload.username,
        hashed_password=__import__("app.core.security", fromlist=["get_password_hash"]).get_password_hash(payload.password),
        full_name=payload.full_name,
        role_id=role.id,
        department_id=payload.department_id,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return await user_to_out(user)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise NotFoundException(message="User not found")
    if current_user.id != user.id and current_user.role.name not in {"super_admin", "admin", "manager"}:
        raise ForbiddenException(message="You do not have access to this user")
    return await user_to_out(user)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise NotFoundException(message="User not found")
    if current_user.id != user.id and current_user.role.name not in {"super_admin", "admin"}:
        raise ForbiddenException(message="You cannot update this user")
    changed_values = payload.model_dump(exclude_unset=True)
    if "role_name" in changed_values:
        role = await db.scalar(select(Role).where(Role.name == changed_values["role_name"]))
        if role is None:
            raise NotFoundException(message=f"Role '{changed_values['role_name']}' not found")
        if role.name in {"admin", "super_admin"} and user.is_active and user.role and user.role.name not in {"admin", "super_admin"}:
            active_admins = await db.scalar(select(User.id).join(Role).where(User.deleted_at.is_(None), User.is_active.is_(True), Role.name.in_(["admin", "super_admin"]), User.id != user.id))
            if active_admins is None:
                raise ForbiddenException(message="Cannot assign the last active administrator to a lower-privilege role")
        user.role_id = role.id
        changed_values.pop("role_name")
    if "is_active" in changed_values and changed_values["is_active"] is False:
        await ensure_admin_protection(db, user)
    for field, value in changed_values.items():
        if field == "password":
            user.hashed_password = __import__("app.core.security", fromlist=["get_password_hash"]).get_password_hash(value)
        else:
            setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return await user_to_out(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin")),
) -> dict[str, str]:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundException(message="User not found")
    if user.role and user.role.name in {"admin", "super_admin"}:
        await ensure_admin_protection(db, user)
    user.deleted_at = __import__("datetime", fromlist=["datetime", "timezone"]).datetime.now(__import__("datetime", fromlist=["timezone"]).timezone.utc)
    await db.commit()
    return {"message": "User deleted successfully"}


@router.put("/{user_id}/roles", response_model=UserOut)
async def assign_role(
    user_id: UUID,
    payload: RoleAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin")),
) -> dict[str, Any]:
    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise NotFoundException(message="User not found")
    role = await db.scalar(select(Role).where(Role.name == payload.role_name))
    if role is None:
        raise NotFoundException(message=f"Role '{payload.role_name}' not found")
    if user.is_active and role.name in {"admin", "super_admin"}:
        admin_count = await db.scalar(
            select(User.id).join(Role).where(
                User.deleted_at.is_(None),
                User.is_active.is_(True),
                Role.name.in_(["admin", "super_admin"]),
                User.id != user.id,
            )
        )
        if admin_count is None:
            raise ForbiddenException(message="Cannot demote the final active administrator")
    user.role_id = role.id
    await db.commit()
    await db.refresh(user)
    return await user_to_out(user)
