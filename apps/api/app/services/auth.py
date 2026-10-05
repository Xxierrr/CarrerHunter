"""
Authentication service: user registration, login, JWT management.
"""

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.models.profile import UserProfile
from app.models.notification import EmailPreference

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, is_admin: bool = False) -> tuple[str, int]:
    """Create a JWT access token. Returns (token, expires_in_seconds)."""
    expires_delta = timedelta(minutes=settings.jwt_access_expiry_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "admin": is_admin,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token."""
    expires_delta = timedelta(days=settings.jwt_refresh_expiry_days)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns payload or None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


async def register_user(
    db: AsyncSession, email: str, password: str, name: str
) -> User:
    """Register a new user with profile and email preferences."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("A user with this email already exists")

    # Create user
    user = User(
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.flush()

    # Create empty profile with name
    profile = UserProfile(user_id=user.id, name=name)
    db.add(profile)

    # Create default email preferences
    email_pref = EmailPreference(user_id=user.id)
    db.add(email_pref)

    await db.flush()
    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    """Authenticate a user by email and password. Returns user or None."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
