from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, date
from typing import Optional, Dict


class RiskAssessment(Document):
    """
    Risk assessment: Probability × Impact.
    Factors: condition + criticality + safety impact + service impact.
    """

    asset_id: PydanticObjectId = Field(...)
    assessment_date: date = Field(default_factory=lambda: date.today())

    # ── Input Factors ────────────────────────────────────────────────────────
    condition_score: float = Field(..., ge=0, le=100)
    condition_rating: str = Field(...)
    criticality: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | CRITICAL")
    safety_impact: str = Field(default="LOW", description="LOW | MEDIUM | HIGH | CRITICAL")
    service_impact: str = Field(default="LOW", description="LOW | MEDIUM | HIGH | CRITICAL")
    environmental_impact: str = Field(default="LOW")

    # ── Computed Risk ────────────────────────────────────────────────────────
    probability: str = Field(default="LOW", description="Probability of failure")
    consequence: str = Field(default="LOW", description="Consequence of failure")
    overall_risk: str = Field(default="LOW", description="LOW | MEDIUM | HIGH | CRITICAL")
    risk_score: float = Field(default=0.0, ge=0, le=100)

    # ── Factors Breakdown ────────────────────────────────────────────────────
    factors: Dict = Field(default_factory=dict, description="Detailed factor breakdown")

    # ── Recommendation ───────────────────────────────────────────────────────
    recommendations: str = Field(default="")
    mitigation_actions: list[str] = Field(default_factory=list)

    # ── Meta ─────────────────────────────────────────────────────────────────
    assessed_by: str = Field(default="System")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "risk_assessments"
