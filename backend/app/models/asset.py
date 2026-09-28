from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict


class AssetLocation(BaseModel):
    """Embedded location data for an asset."""
    district: str = ""
    taluka: str = ""
    city: str = ""
    address: str = ""
    pin_code: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AssetResponsibility(BaseModel):
    """Who is responsible for the asset."""
    custodian: str = Field(default="Roads & Buildings Department")
    operator: str = Field(default="")
    maintenance_agency: str = Field(default="")


class PlannedLifecycle(BaseModel):
    """What SHOULD happen — planned intervals."""
    inspection_interval_days: int = Field(default=365, description="Expected inspection every N days")
    preservation_interval_years: Optional[int] = Field(default=None)
    rehabilitation_condition_threshold: int = Field(
        default=40, description="Condition score below which rehabilitation is needed"
    )
    expected_useful_life_years: Optional[int] = Field(default=None)


class Asset(Document):
    """
    A PHYSICAL ASSET that persists long after the project ends.
    This is the core entity — the Digital Asset Passport.
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    code: str = Field(..., description="Unique asset code, e.g., R&B-BLD-00021")
    name: str = Field(..., description="Asset name")
    description: str = Field(default="")

    # ── Classification ───────────────────────────────────────────────────────
    infrastructure_class_id: PydanticObjectId = Field(...)
    infrastructure_class_code: str = Field(
        ..., description="Denormalized: BUILDING / ROAD / BRIDGE"
    )
    asset_type_id: PydanticObjectId = Field(...)
    asset_type_name: str = Field(default="")

    # ── Project Link ─────────────────────────────────────────────────────────
    project_id: Optional[PydanticObjectId] = Field(
        default=None, description="The project that created this asset"
    )
    project_code: str = Field(default="", description="Denormalized project code")

    # ── Lifecycle ────────────────────────────────────────────────────────────
    lifecycle_template_id: Optional[PydanticObjectId] = Field(default=None)
    current_stage: str = Field(default="CREATED", description="Current lifecycle stage")
    previous_stage: Optional[str] = Field(default=None)

    # ── Location ─────────────────────────────────────────────────────────────
    location: AssetLocation = Field(default_factory=AssetLocation)

    # ── Dates ────────────────────────────────────────────────────────────────
    commissioned_date: Optional[date] = None
    handover_date: Optional[date] = None
    warranty_expiry: Optional[date] = None

    # ── Responsibility ───────────────────────────────────────────────────────
    responsibility: AssetResponsibility = Field(default_factory=AssetResponsibility)

    # ── Condition (latest snapshot) ──────────────────────────────────────────
    current_condition_score: Optional[float] = Field(
        default=None, ge=0, le=100, description="0-100 condition score"
    )
    current_condition_rating: str = Field(
        default="NOT_ASSESSED",
        description="GOOD | FAIR | POOR | CRITICAL | NOT_ASSESSED",
    )

    # ── Performance (infra-specific) ─────────────────────────────────────────
    performance_metrics: Dict[str, str] = Field(
        default_factory=dict,
        description="Infrastructure-specific performance data, e.g., traffic, occupancy, load",
    )

    # ── Risk ─────────────────────────────────────────────────────────────────
    current_risk_level: str = Field(default="NOT_ASSESSED", description="LOW | MEDIUM | HIGH | CRITICAL")
    risk_score: Optional[float] = Field(default=None)

    # ── Next Action ──────────────────────────────────────────────────────────
    next_action: Optional[str] = Field(default=None, description="Recommended next action")
    next_action_due: Optional[date] = Field(default=None)
    next_action_priority: str = Field(default="NORMAL", description="LOW | NORMAL | HIGH | URGENT")

    # ── Inspection ───────────────────────────────────────────────────────────
    last_inspection_date: Optional[date] = None
    next_inspection_due: Optional[date] = None

    # ── Value ────────────────────────────────────────────────────────────────
    estimated_value: float = Field(default=0.0, description="Asset value in ₹ Cr")
    replacement_value: float = Field(default=0.0)

    # ── Planned Lifecycle ────────────────────────────────────────────────────
    planned_lifecycle: PlannedLifecycle = Field(default_factory=PlannedLifecycle)

    # ── Photographs ──────────────────────────────────────────────────────────
    photographs: List[str] = Field(default_factory=list)

    # ── Infra-specific metadata ──────────────────────────────────────────────
    metadata: Dict = Field(
        default_factory=dict,
        description="Infrastructure-class-specific fields (road: length_km, lanes, surface_type; building: floors, area_sqm; bridge: span_m, deck_type)",
    )

    # ── Status ───────────────────────────────────────────────────────────────
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "assets"
