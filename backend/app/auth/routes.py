from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.auth.models import User
from app.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = "viewer"
    department: str = "Roads & Buildings Department"
    designation: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    department: str
    designation: Optional[str] = None
    is_active: bool
    created_at: datetime


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    """Register a new user."""
    existing = await User.find_one(
        {"$or": [{"username": data.username}, {"email": data.email}]}
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        department=data.department,
        designation=data.designation,
    )
    await user.insert()

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department=user.department,
        designation=user.designation,
        is_active=user.is_active,
        created_at=user.created_at,
    )


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login with JSON payload and receive JWT token. Supports login by username or email."""
    user = await User.find_one(User.username == login_data.username)
    if not user:
        user = await User.find_one(User.email == login_data.username)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    return LoginResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "designation": user.designation,
        },
    )


@router.post("/token", response_model=LoginResponse)
async def token_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login for Swagger UI."""
    user = await User.find_one(User.username == form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    return LoginResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "designation": user.designation,
        },
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the current authenticated user profile."""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        department=current_user.department,
        designation=current_user.designation,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.get("/users", response_model=list[UserResponse])
async def list_users(current_user: User = Depends(get_current_user)):
    """List all users (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    users = await User.find_all().to_list()
    return [
        UserResponse(
            id=str(u.id),
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            department=u.department,
            designation=u.designation,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]
