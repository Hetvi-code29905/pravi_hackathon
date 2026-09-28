"""Routes for Infrastructure Classes and Asset Types — the classification layer."""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from beanie import PydanticObjectId

from app.models.infrastructure import InfrastructureClass
from app.models.asset_type import AssetType
from app.auth.utils import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/api/infrastructure", tags=["Infrastructure"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class InfraClassResponse(BaseModel):
    id: str
    code: str
    name: str
    description: str
    icon: str
    color: str
    is_active: bool
    asset_type_count: int = 0


class AssetTypeResponse(BaseModel):
    id: str
    code: str
    name: str
    infrastructure_class_id: str
    infrastructure_class_code: str
    description: str
    default_inspection_interval_days: int
    is_active: bool


class AssetTypeCreate(BaseModel):
    code: str
    name: str
    infrastructure_class_id: str
    description: str = ""
    default_inspection_interval_days: int = 365


# ── Infrastructure Class Routes ──────────────────────────────────────────────

@router.get("/classes", response_model=List[InfraClassResponse])
async def list_infrastructure_classes(current_user: User = Depends(get_current_user)):
    """List all infrastructure classes (Building, Road, Bridge)."""
    classes = await InfrastructureClass.find(
        InfrastructureClass.is_active == True
    ).to_list()

    result = []
    for cls in classes:
        count = await AssetType.find(
            AssetType.infrastructure_class_id == cls.id,
            AssetType.is_active == True,
        ).count()
        result.append(
            InfraClassResponse(
                id=str(cls.id),
                code=cls.code,
                name=cls.name,
                description=cls.description,
                icon=cls.icon,
                color=cls.color,
                is_active=cls.is_active,
                asset_type_count=count,
            )
        )
    return result


@router.get("/classes/{class_id}", response_model=InfraClassResponse)
async def get_infrastructure_class(class_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific infrastructure class."""
    cls = await InfrastructureClass.get(PydanticObjectId(class_id))
    if not cls:
        raise HTTPException(status_code=404, detail="Infrastructure class not found")

    count = await AssetType.find(AssetType.infrastructure_class_id == cls.id).count()
    return InfraClassResponse(
        id=str(cls.id),
        code=cls.code,
        name=cls.name,
        description=cls.description,
        icon=cls.icon,
        color=cls.color,
        is_active=cls.is_active,
        asset_type_count=count,
    )


# ── Asset Type Routes ────────────────────────────────────────────────────────

@router.get("/types", response_model=List[AssetTypeResponse])
@router.get("/asset-types", response_model=List[AssetTypeResponse])
async def list_asset_types(
    infrastructure_class_code: Optional[str] = None,
    infrastructure_class_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """List asset types, optionally filtered by infrastructure class."""
    query = {"is_active": True}
    if infrastructure_class_code:
        query["infrastructure_class_code"] = infrastructure_class_code
    if infrastructure_class_id:
        query["infrastructure_class_id"] = PydanticObjectId(infrastructure_class_id)

    types = await AssetType.find(query).to_list()
    return [
        AssetTypeResponse(
            id=str(t.id),
            code=t.code,
            name=t.name,
            infrastructure_class_id=str(t.infrastructure_class_id),
            infrastructure_class_code=t.infrastructure_class_code,
            description=t.description,
            default_inspection_interval_days=t.default_inspection_interval_days,
            is_active=t.is_active,
        )
        for t in types
    ]


@router.get("/types/{type_id}", response_model=AssetTypeResponse)
async def get_asset_type(type_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific asset type."""
    t = await AssetType.get(PydanticObjectId(type_id))
    if not t:
        raise HTTPException(status_code=404, detail="Asset type not found")
    return AssetTypeResponse(
        id=str(t.id),
        code=t.code,
        name=t.name,
        infrastructure_class_id=str(t.infrastructure_class_id),
        infrastructure_class_code=t.infrastructure_class_code,
        description=t.description,
        default_inspection_interval_days=t.default_inspection_interval_days,
        is_active=t.is_active,
    )
