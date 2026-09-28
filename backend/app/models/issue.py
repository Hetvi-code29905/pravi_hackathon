from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime, date
from typing import Optional


class Issue(Document):
    """Tracked issue or defect for an asset."""

    asset_id: PydanticObjectId = Field(...)
    title: str = Field(...)
    description: str = Field(default="")
    severity: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | CRITICAL")
    status: str = Field(
        default="OPEN", description="OPEN | INVESTIGATING | IN_PROGRESS | RESOLVED | CLOSED"
    )
    category: str = Field(default="GENERAL", description="STRUCTURAL | ELECTRICAL | PLUMBING | SAFETY | GENERAL")
    reported_by: str = Field(default="")
    reported_date: date = Field(default_factory=lambda: date.today())
    assigned_to: str = Field(default="")
    resolved_date: Optional[date] = None
    resolution: str = Field(default="")
    resolution_notes: Optional[str] = Field(default=None)
    resolved_at: Optional[datetime] = Field(default=None)
    linked_inspection_id: Optional[PydanticObjectId] = None
    linked_maintenance_id: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "issues"
