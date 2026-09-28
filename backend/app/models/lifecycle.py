from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class LifecycleStageDefinition(BaseModel):
    """A single stage within a lifecycle template."""
    code: str = Field(..., description="Stage code, e.g., OPERATIONAL")
    name: str = Field(..., description="Display name")
    description: str = Field(default="")
    order: int = Field(..., description="Display order")
    stage_type: str = Field(
        default="normal",
        description="normal | initial | terminal | loop",
    )
    is_terminal: bool = Field(default=False, description="If true, this is the final stage")


class LifecycleTransitionRule(BaseModel):
    """Allowed transition between lifecycle stages."""
    from_stage: str
    to_stage: str
    requires_condition_assessment: bool = Field(default=False)
    requires_inspection: bool = Field(default=False)
    required_fields: List[str] = Field(default_factory=list)
    description: str = Field(default="")


class ConditionThreshold(BaseModel):
    """Maps condition scores to ratings and recommended actions."""
    min_score: int
    max_score: int
    rating: str  # GOOD, FAIR, POOR, CRITICAL
    recommended_action: str
    color: str = "#22C55E"


class LifecycleTemplate(Document):
    """
    Configurable lifecycle state machine per infrastructure class.
    Building ≠ Road ≠ Bridge — each has unique stages, transitions, and thresholds.
    """

    code: str = Field(..., description="Template code, e.g., BUILDING_LIFECYCLE")
    name: str = Field(..., description="Display name")
    infrastructure_class_code: str = Field(
        ..., description="BUILDING | ROAD | BRIDGE"
    )
    description: str = Field(default="")

    # ── State Machine ────────────────────────────────────────────────────────
    stages: List[LifecycleStageDefinition] = Field(default_factory=list)
    transitions: List[LifecycleTransitionRule] = Field(default_factory=list)

    # ── Condition Thresholds ─────────────────────────────────────────────────
    condition_thresholds: List[ConditionThreshold] = Field(default_factory=list)

    # ── Meta ─────────────────────────────────────────────────────────────────
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lifecycle_templates"


class LifecycleEvent(Document):
    """
    Audit trail: every lifecycle transition is recorded as an immutable event.
    """

    asset_id: PydanticObjectId = Field(...)
    from_stage: str = Field(...)
    to_stage: str = Field(...)
    transition_date: datetime = Field(default_factory=datetime.utcnow)
    performed_by: str = Field(default="System")
    notes: str = Field(default="")
    metadata: dict = Field(default_factory=dict, description="Extra data at transition time")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lifecycle_events"
