from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash, hash_token, revoke_token, revoked_tokens, verify_password
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, PasswordChangeRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user_row = await db.execute(
        select(User).options(selectinload(User.role)).where(
            or_(User.email == str(payload.email), User.username == str(payload.email))
        )
    )
    user = user_row.scalar_one_or_none()
    if user is None or not user.is_active or user.deleted_at is not None:
        raise UnauthorizedException(message="Invalid credentials")
    if not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedException(message="Invalid credentials")

    role = user.role
    if role is None:
        raise UnauthorizedException(message="User role not configured")

    access_token = create_access_token(str(user.id), role.name)
    refresh_token = create_refresh_token(str(user.id))
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user: User = Depends(get_current_user)) -> dict[str, object]:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role_name": current_user.role_name,
        "department_id": current_user.department_id,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise UnauthorizedException(message="Invalid refresh token")
    if hash_token(payload.refresh_token) in revoked_tokens:
        raise UnauthorizedException(message="Refresh token has been revoked")
    user_id = decoded.get("sub")
    if not user_id:
        raise UnauthorizedException(message="Invalid refresh payload")
    user_row = await db.execute(select(User).options(selectinload(User.role)).where(User.id == UUID(str(user_id))))
    user = user_row.scalar_one_or_none()
    if user is None or not user.is_active or user.deleted_at is not None:
        raise UnauthorizedException(message="User no longer active")
    role = user.role
    if role is None:
        raise UnauthorizedException(message="User role not configured")
    revoke_token(payload.refresh_token)
    return TokenResponse(
        access_token=create_access_token(str(user.id), role.name),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/logout")
async def logout(
    payload: RefreshTokenRequest | None = None,
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if credentials and credentials.credentials:
        revoke_token(credentials.credentials)
    if payload and payload.refresh_token:
        revoke_token(payload.refresh_token)
    return {"message": f"User {current_user.email} logged out successfully"}


@router.put("/change-password")
async def change_password(
    payload: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise ForbiddenException(message="Current password is incorrect")
    current_user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()
    return {"message": "Password updated successfully"}
