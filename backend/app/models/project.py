from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List


class ProjectLocation(BaseModel):
    """Embedded location data for a project."""
    district: str = ""
    taluka: str = ""
    city: str = ""
    address: str = ""
    pin_code: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Project(Document):
    """
    A project is TEMPORARY — it has a beginning and end.
    Project lifecycle: NEED → PLANNING → DESIGN → TENDER → CONSTRUCTION → COMMISSIONING → HANDOVER → CLOSED
    Once a project is completed, it creates a Physical Asset.
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    code: str = Field(..., description="Unique project code, e.g., PRJ-RNB-2026-0001")
    name: str = Field(..., description="Project name")
    description: str = Field(default="")

    # ── Classification ───────────────────────────────────────────────────────
    infrastructure_class_id: PydanticObjectId = Field(...)
    infrastructure_class_code: str = Field(
        ..., description="Denormalized: BUILDING / ROAD / BRIDGE"
    )
    asset_type_id: PydanticObjectId = Field(...)
    asset_type_name: str = Field(default="", description="Denormalized asset type name")

    # ── Project Lifecycle ────────────────────────────────────────────────────
    status: str = Field(
        default="NEED",
        description="NEED | PLANNING | DESIGN | TENDER | CONSTRUCTION | QUALITY_ACCEPTANCE | COMMISSIONING | HANDOVER | CLOSED",
    )

    # ── Location ─────────────────────────────────────────────────────────────
    location: ProjectLocation = Field(default_factory=ProjectLocation)

    # ── Cost ─────────────────────────────────────────────────────────────────
    estimated_cost: float = Field(default=0.0, description="Estimated cost in ₹ Cr")
    sanctioned_cost: float = Field(default=0.0, description="Sanctioned cost in ₹ Cr")
    actual_cost: float = Field(default=0.0, description="Actual cost in ₹ Cr")

    # ── Dates ────────────────────────────────────────────────────────────────
    start_date: Optional[date] = None
    expected_completion: Optional[date] = None
    actual_completion: Optional[date] = None

    # ── Responsibility ───────────────────────────────────────────────────────
    contractor: str = Field(default="")
    supervising_officer: str = Field(default="")
    department: str = Field(default="Roads & Buildings Department")

    # ── Linked Asset ─────────────────────────────────────────────────────────
    asset_id: Optional[PydanticObjectId] = Field(
        default=None, description="Physical asset created from this project"
    )

    # ── Meta ─────────────────────────────────────────────────────────────────
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "projects"
