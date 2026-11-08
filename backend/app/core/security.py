"""Security utilities: password hashing with bcrypt, JWT creation and verification, token hashing."""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.constants import ErrorCode
from app.core.exceptions import UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
revoked_tokens: set[str] = set()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash from plain password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a short-lived signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid4()),
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a longer-lived JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid4()),
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def revoke_token(token: str) -> None:
    """Mark a token as revoked so the app rejects it after logout or rotation."""
    if token:
        revoked_tokens.add(hash_token(token))


def is_token_revoked(token: str) -> bool:
    """Check whether a token has already been invalidated."""
    return bool(token) and hash_token(token) in revoked_tokens


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token payload."""
    try:
        if is_token_revoked(token):
            raise UnauthorizedException(message="Token has been revoked", code=ErrorCode.INVALID_TOKEN)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except UnauthorizedException:
        raise
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(message="Token has expired", code=ErrorCode.TOKEN_EXPIRED)
    except JWTError:
        raise UnauthorizedException(message="Could not validate credentials", code=ErrorCode.INVALID_TOKEN)


def hash_token(token: str) -> str:
    """Generate SHA-256 hash of a token string for safe database persistence."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

