from __future__ import annotations

from typing import Callable
from uuid import UUID

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import RoleEnum
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token, is_token_revoked
from app.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedException(message="Authentication required")
    if is_token_revoked(credentials.credentials):
        raise UnauthorizedException(message="Token has been revoked")

    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise UnauthorizedException(message="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(message="Invalid token payload")

    user = (await db.execute(select(User).where(User.id == UUID(str(user_id))).options(selectinload(User.role))))
    user = user.scalar_one_or_none()
    if user is None or not user.is_active or user.deleted_at is not None:
        raise UnauthorizedException(message="User not found or inactive")

    return user


def require_roles(*allowed_roles: str):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        role_name = current_user.role.name if current_user.role else ""
        if role_name in allowed_roles or "*" in (current_user.role.permissions if current_user.role else []):
            return current_user
        raise ForbiddenException(message=f"Role '{role_name}' is not permitted", status_code=status.HTTP_403_FORBIDDEN)

    return dependency


def require_permissions(*required_permissions: str):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        permissions = set(current_user.role.permissions if current_user.role else [])
        if "*" in permissions or all(permission in permissions for permission in required_permissions):
            return current_user
        raise ForbiddenException(message="Missing required permissions", status_code=status.HTTP_403_FORBIDDEN)

    return dependency
