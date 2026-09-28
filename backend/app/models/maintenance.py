from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, date
from typing import Optional


class MaintenanceRecord(Document):
    """
    Maintenance / intervention record.
    Types range from ROUTINE to RECONSTRUCTION, matching real infrastructure practice.
    """

    asset_id: PydanticObjectId = Field(...)

    # ── Type & Classification ────────────────────────────────────────────────
    maintenance_type: str = Field(
        ...,
        description="ROUTINE | PREVENTIVE | CORRECTIVE | REPAIR | REHABILITATION | RENEWAL | RECONSTRUCTION",
    )
    title: str = Field(...)
    description: str = Field(default="")

    # ── Priority & Status ────────────────────────────────────────────────────
    priority: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | URGENT")
    status: str = Field(
        default="PLANNED",
        description="PLANNED | SCHEDULED | IN_PROGRESS | COMPLETED | CANCELLED",
    )

    # ── Cost ─────────────────────────────────────────────────────────────────
    estimated_cost: float = Field(default=0.0, description="Estimated cost in ₹ Lakhs")
    actual_cost: float = Field(default=0.0, description="Actual cost in ₹ Lakhs")

    # ── Schedule ─────────────────────────────────────────────────────────────
    scheduled_date: Optional[date] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None

    # ── Responsibility ───────────────────────────────────────────────────────
    assigned_agency: str = Field(default="")
    performed_by: str = Field(default="")
    approved_by: str = Field(default="")

    # ── Outcome ──────────────────────────────────────────────────────────────
    work_done: str = Field(default="", description="Description of work performed")
    notes: str = Field(default="")
    condition_after: Optional[str] = Field(default=None, description="Condition rating post-maintenance")

    # ── Triggered By ─────────────────────────────────────────────────────────
    triggered_by_inspection_id: Optional[PydanticObjectId] = Field(default=None)
    triggered_by_condition: Optional[str] = Field(default=None)

    # ── Meta ─────────────────────────────────────────────────────────────────
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "maintenance_records"
