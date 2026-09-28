from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class InfrastructureClass(Document):
    """
    Top-level infrastructure classification.
    Three classes for Gujarat R&B: BUILDING, ROAD, BRIDGE.
    """

    code: str = Field(..., description="Unique code: BUILDING, ROAD, BRIDGE")
    name: str = Field(..., description="Display name")
    description: str = Field(default="", description="Class description")
    icon: str = Field(default="🏗️", description="Display icon/emoji")
    color: str = Field(default="#3B82F6", description="Theme color hex code")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "infrastructure_classes"
