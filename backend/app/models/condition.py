from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, date
from typing import Optional, Dict


class ConditionAssessment(Document):
    """
    Historical condition record — we store EVERY assessment, not just current state.
    This enables trend tracking: Good → Good → Fair → Poor.
    """

    asset_id: PydanticObjectId = Field(...)
    assessment_date: date = Field(...)
    
    # ── Scores ───────────────────────────────────────────────────────────────
    overall_score: float = Field(..., ge=0, le=100, description="Overall condition 0-100")
    overall_rating: str = Field(..., description="GOOD | FAIR | POOR | CRITICAL")

    # ── Multi-dimensional condition ──────────────────────────────────────────
    structural_condition: str = Field(default="NOT_ASSESSED", description="GOOD | FAIR | POOR | CRITICAL")
    structural_score: Optional[float] = Field(default=None, ge=0, le=100)
    functional_condition: str = Field(default="NOT_ASSESSED")
    functional_score: Optional[float] = Field(default=None, ge=0, le=100)
    safety_condition: str = Field(default="NOT_ASSESSED")
    safety_score: Optional[float] = Field(default=None, ge=0, le=100)

    # ── Details ──────────────────────────────────────────────────────────────
    inspector: str = Field(default="")
    findings: str = Field(default="")
    recommendations: str = Field(default="")

    # ── Infrastructure-specific performance ──────────────────────────────────
    performance_data: Dict = Field(
        default_factory=dict,
        description="Infra-specific metrics: road={pavement, drainage, traffic}; bridge={deck, substructure, load}; building={electrical, plumbing, fire_safety, occupancy}",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "condition_assessments"
