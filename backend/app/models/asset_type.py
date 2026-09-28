from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime
from typing import Optional


class AssetType(Document):
    """
    Sub-classification under an infrastructure class.
    E.g., Government Hospital, State Highway, Major Bridge.
    """

    code: str = Field(..., description="Unique type code, e.g., GOVT_HOSPITAL")
    name: str = Field(..., description="Display name")
    infrastructure_class_id: PydanticObjectId = Field(
        ..., description="Reference to parent InfrastructureClass"
    )
    infrastructure_class_code: str = Field(
        ..., description="Denormalized class code for quick queries"
    )
    description: str = Field(default="")
    default_inspection_interval_days: int = Field(
        default=365, description="Default inspection interval in days"
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "asset_types"
