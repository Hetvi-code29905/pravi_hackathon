# pyrefly: ignore [missing-import]
from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class User(Document):
    """User model for authentication and RBAC."""

    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: str = Field(..., description="User email address")
    password_hash: str = Field(..., description="Hashed password")
    full_name: str = Field(..., description="Full name of the user")
    role: str = Field(
        default="viewer",
        description="User role: admin, chief_engineer, executive_engineer, inspector, viewer",
    )
    department: str = Field(default="Roads & Buildings Department")
    designation: Optional[str] = Field(default=None, description="Official designation")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "email": "admin@rnb.gov.in",
                "full_name": "System Administrator",
                "role": "admin",
                "department": "Roads & Buildings Department",
            }
        }
