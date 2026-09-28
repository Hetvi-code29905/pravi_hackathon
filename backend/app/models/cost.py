from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, date
from typing import Optional


class AssetCost(Document):
    """
    Lifecycle cost tracking — distinguishes capital, maintenance, repair, rehabilitation, etc.
    Supports whole-life-cost thinking in infrastructure asset management.
    """

    asset_id: PydanticObjectId = Field(...)
    cost_type: str = Field(
        ...,
        description="CAPITAL | MAINTENANCE | REPAIR | REHABILITATION | REPLACEMENT | INSPECTION | OTHER",
    )
    description: str = Field(default="")
    amount: float = Field(..., description="Amount in ₹ Lakhs")
    currency: str = Field(default="INR")
    financial_year: str = Field(default="", description="e.g., 2026-27")
    date_incurred: Optional[date] = None
    source_of_funds: str = Field(default="", description="Budget head / scheme")
    approved_by: str = Field(default="")
    linked_maintenance_id: Optional[PydanticObjectId] = None
    notes: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "asset_costs"
