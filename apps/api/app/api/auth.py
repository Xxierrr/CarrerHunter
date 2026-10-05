"""
Authentication API routes: register, login, refresh, logout.
"""

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_by_id,
    register_user,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: DbSession):
    """Register a new user account."""
    try:
        user = await register_user(db, request.email, request.password, request.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    access_token, expires_in = create_access_token(str(user.id), user.is_admin)
    refresh_token = create_refresh_token(str(user.id))

    # Load the profile to get the name
    await db.refresh(user, ["profile"])

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.profile.name if user.profile else request.name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: DbSession):
    """Login with email and password."""
    user = await authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token, expires_in = create_access_token(str(user.id), user.is_admin)

    # Load profile for name
    await db.refresh(user, ["profile"])

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.profile.name if user.profile else None,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            created_at=user.created_at,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, db: DbSession):
    """Refresh an access token using a refresh token."""
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    import uuid
    user = await get_user_by_id(db, uuid.UUID(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token, expires_in = create_access_token(str(user.id), user.is_admin)

    await db.refresh(user, ["profile"])

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.profile.name if user.profile else None,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_admin=user.is_admin,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser, db: DbSession):
    """Get the current authenticated user."""
    await db.refresh(current_user, ["profile"])
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.profile.name if current_user.profile else None,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
    )
