from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, date
from typing import Optional


class AssetComponent(Document):
    """
    Sub-component of a physical asset.
    Buildings have electrical/HVAC/plumbing, bridges have deck/piers/abutments, etc.
    """
    model_config = {"protected_namespaces": ()}

    asset_id: PydanticObjectId = Field(...)
    name: str = Field(...)
    component_type: str = Field(
        ..., description="STRUCTURAL | ELECTRICAL | MECHANICAL | PLUMBING | HVAC | DECK | PIER | ABUTMENT | RAILING | PAVEMENT | DRAINAGE | OTHER"
    )
    description: str = Field(default="")
    condition: str = Field(default="NOT_ASSESSED", description="GOOD | FAIR | POOR | CRITICAL | NOT_ASSESSED")
    condition_score: Optional[float] = Field(default=None, ge=0, le=100)
    installed_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    manufacturer: str = Field(default="")
    model_number: str = Field(default="")
    notes: str = Field(default="")
    is_critical: bool = Field(default=False, description="If true, failure of this component is high-impact")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "asset_components"
