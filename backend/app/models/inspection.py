from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, date
from typing import Optional, List


class Inspection(Document):
    """
    Inspection record — distinct from condition assessment.
    Inspections FEED condition assessments and drive lifecycle decisions.
    """

    asset_id: PydanticObjectId = Field(...)

    # ── Type & Schedule ──────────────────────────────────────────────────────
    inspection_type: str = Field(
        ..., description="ROUTINE | INITIAL | SPECIAL | EMERGENCY | PERIODIC"
    )
    inspection_date: date = Field(...)
    
    # ── Inspector ────────────────────────────────────────────────────────────
    inspector_name: str = Field(...)
    inspector_designation: str = Field(default="")
    inspector_agency: str = Field(default="")

    # ── Condition Findings ───────────────────────────────────────────────────
    overall_condition: str = Field(default="NOT_ASSESSED", description="GOOD | FAIR | POOR | CRITICAL")
    condition_score: Optional[float] = Field(default=None, ge=0, le=100)
    structural_condition: str = Field(default="NOT_ASSESSED")
    functional_condition: str = Field(default="NOT_ASSESSED")
    safety_condition: str = Field(default="NOT_ASSESSED")

    # ── Narrative ────────────────────────────────────────────────────────────
    findings: str = Field(default="", description="Detailed inspection findings")
    recommendations: str = Field(default="", description="Recommended actions")
    defects_found: List[str] = Field(default_factory=list, description="List of defects identified")

    # ── Next Steps ───────────────────────────────────────────────────────────
    next_inspection_date: Optional[date] = Field(default=None)
    requires_immediate_action: bool = Field(default=False)
    immediate_action_description: str = Field(default="")

    # ── Photos ───────────────────────────────────────────────────────────────
    photographs: List[str] = Field(default_factory=list)

    # ── Meta ─────────────────────────────────────────────────────────────────
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "inspections"
