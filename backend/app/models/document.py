from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime
from typing import Optional


class AssetDocument(Document):
    """Document/attachment linked to an asset — drawings, reports, photos, certificates."""

    asset_id: PydanticObjectId = Field(...)
    title: str = Field(...)
    document_type: str = Field(
        ..., description="DRAWING | REPORT | CERTIFICATE | PHOTOGRAPH | TENDER | CONTRACT | AS_BUILT | INSPECTION_REPORT | OTHER"
    )
    description: str = Field(default="")
    file_name: str = Field(default="")
    file_url: str = Field(default="", description="URL or path to the document")
    file_size: str = Field(default="")
    uploaded_by: str = Field(default="")
    version: str = Field(default="1.0")
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "documents"
