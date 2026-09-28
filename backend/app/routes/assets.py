"""
Asset routes — The Digital Asset Passport.
CRUD + lifecycle + condition + timeline.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date
from beanie import PydanticObjectId

from app.models.asset import Asset, AssetLocation, AssetResponsibility, PlannedLifecycle
from app.models.lifecycle import LifecycleTemplate, LifecycleEvent
from app.models.condition import ConditionAssessment
from app.models.inspection import Inspection
from app.models.maintenance import MaintenanceRecord
from app.models.issue import Issue
from app.models.component import AssetComponent
from app.models.document import AssetDocument
from app.models.risk import RiskAssessment
from app.models.cost import AssetCost
from app.services.lifecycle_engine import (
    get_allowed_transitions,
    execute_transition,
    get_lifecycle_timeline,
    get_current_stage_info,
)
from app.auth.utils import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/api/assets", tags=["Assets"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class AssetCreate(BaseModel):
    name: str
    description: str = ""
    infrastructure_class_id: str
    asset_type_id: str
    location: Optional[dict] = None
    commissioned_date: Optional[date] = None
    custodian: str = "Roads & Buildings Department"
    operator: str = ""
    maintenance_agency: str = ""
    estimated_value: float = 0.0
    metadata: dict = {}


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[dict] = None
    custodian: Optional[str] = None
    operator: Optional[str] = None
    maintenance_agency: Optional[str] = None
    estimated_value: Optional[float] = None
    replacement_value: Optional[float] = None
    metadata: Optional[dict] = None
    performance_metrics: Optional[Dict[str, str]] = None


class TransitionRequest(BaseModel):
    to_stage: str
    notes: str = ""
    metadata: dict = {}


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("")
async def list_assets(
    infrastructure_class_code: Optional[str] = None,
    asset_type_id: Optional[str] = None,
    current_stage: Optional[str] = None,
    condition_rating: Optional[str] = None,
    risk_level: Optional[str] = None,
    district: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    current_user: User = Depends(get_current_user),
):
    """List assets with comprehensive filters."""
    query = {"is_active": True}

    if infrastructure_class_code:
        query["infrastructure_class_code"] = infrastructure_class_code
    if asset_type_id:
        query["asset_type_id"] = PydanticObjectId(asset_type_id)
    if current_stage:
        query["current_stage"] = current_stage
    if condition_rating:
        query["current_condition_rating"] = condition_rating
    if risk_level:
        query["current_risk_level"] = risk_level
    if district:
        query["location.district"] = district
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"code": {"$regex": search, "$options": "i"}},
            {"location.city": {"$regex": search, "$options": "i"}},
            {"location.district": {"$regex": search, "$options": "i"}},
        ]

    assets = await Asset.find(query).skip(skip).limit(limit).sort("-updated_at").to_list()
    total = await Asset.find(query).count()

    return {
        "items": [_asset_to_dict(a) for a in assets],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{asset_id}")
async def get_asset(asset_id: str, current_user: User = Depends(get_current_user)):
    """Get full asset passport — the primary detail view."""
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Get related data counts
    inspections_count = await Inspection.find(Inspection.asset_id == asset.id).count()
    maintenance_count = await MaintenanceRecord.find(MaintenanceRecord.asset_id == asset.id).count()
    issues_count = await Issue.find(Issue.asset_id == asset.id).count()
    components_count = await AssetComponent.find(AssetComponent.asset_id == asset.id).count()
    documents_count = await AssetDocument.find(AssetDocument.asset_id == asset.id).count()

    # Get lifecycle info
    stage_info = await get_current_stage_info(asset)
    allowed = await get_allowed_transitions(asset)

    result = _asset_to_dict(asset)
    result["stage_info"] = stage_info
    result["allowed_transitions"] = allowed
    result["counts"] = {
        "inspections": inspections_count,
        "maintenance": maintenance_count,
        "issues": issues_count,
        "components": components_count,
        "documents": documents_count,
    }

    return result


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_asset(data: AssetCreate, current_user: User = Depends(get_current_user)):
    """Create a standalone asset (not from a project)."""
    from app.models.infrastructure import InfrastructureClass
    from app.models.asset_type import AssetType as AT

    infra_class = await InfrastructureClass.get(PydanticObjectId(data.infrastructure_class_id))
    if not infra_class:
        raise HTTPException(status_code=400, detail="Invalid infrastructure class")

    asset_type = await AT.get(PydanticObjectId(data.asset_type_id))
    if not asset_type:
        raise HTTPException(status_code=400, detail="Invalid asset type")

    template = await LifecycleTemplate.find_one(
        LifecycleTemplate.infrastructure_class_code == infra_class.code,
        LifecycleTemplate.is_active == True,
    )

    prefix_map = {"BUILDING": "BLD", "ROAD": "RD", "BRIDGE": "BRG"}
    prefix = prefix_map.get(infra_class.code, "AST")
    count = await Asset.find(Asset.infrastructure_class_code == infra_class.code).count()
    asset_code = f"R&B-{prefix}-{str(count + 1).zfill(5)}"

    location = AssetLocation(**(data.location or {}))

    asset = Asset(
        code=asset_code,
        name=data.name,
        description=data.description,
        infrastructure_class_id=infra_class.id,
        infrastructure_class_code=infra_class.code,
        asset_type_id=asset_type.id,
        asset_type_name=asset_type.name,
        lifecycle_template_id=template.id if template else None,
        current_stage="CREATED",
        location=location,
        commissioned_date=data.commissioned_date,
        responsibility=AssetResponsibility(
            custodian=data.custodian,
            operator=data.operator,
            maintenance_agency=data.maintenance_agency,
        ),
        estimated_value=data.estimated_value,
        metadata=data.metadata,
        planned_lifecycle=PlannedLifecycle(),
    )
    await asset.insert()

    event = LifecycleEvent(
        asset_id=asset.id,
        from_stage="NONE",
        to_stage="CREATED",
        performed_by=current_user.username,
        notes="Asset created directly",
    )
    await event.insert()

    return _asset_to_dict(asset)


@router.patch("/{asset_id}")
async def update_asset(
    asset_id: str,
    data: AssetUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update asset details."""
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    update_data = data.model_dump(exclude_none=True)

    if "location" in update_data:
        update_data["location"] = AssetLocation(**update_data["location"])
    if "custodian" in update_data or "operator" in update_data or "maintenance_agency" in update_data:
        resp = asset.responsibility.model_dump()
        for key in ["custodian", "operator", "maintenance_agency"]:
            if key in update_data:
                resp[key] = update_data.pop(key)
        update_data["responsibility"] = AssetResponsibility(**resp)

    for key, value in update_data.items():
        setattr(asset, key, value)

    asset.updated_at = datetime.utcnow()
    await asset.save()
    return _asset_to_dict(asset)


# ── Lifecycle Routes ─────────────────────────────────────────────────────────

@router.get("/{asset_id}/lifecycle")
async def get_asset_lifecycle(asset_id: str, current_user: User = Depends(get_current_user)):
    """Get lifecycle state, allowed transitions, and template info."""
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    stage_info = await get_current_stage_info(asset)
    allowed = await get_allowed_transitions(asset)

    template = None
    if asset.lifecycle_template_id:
        tmpl = await LifecycleTemplate.get(asset.lifecycle_template_id)
        if tmpl:
            template = {
                "id": str(tmpl.id),
                "name": tmpl.name,
                "code": tmpl.code,
                "stages": [s.model_dump() for s in tmpl.stages],
                "condition_thresholds": [t.model_dump() for t in tmpl.condition_thresholds],
            }

    return {
        "current_stage": asset.current_stage,
        "previous_stage": asset.previous_stage,
        "stage_info": stage_info,
        "allowed_transitions": allowed,
        "template": template,
    }


@router.post("/{asset_id}/lifecycle/transition")
async def transition_asset(
    asset_id: str,
    data: TransitionRequest,
    current_user: User = Depends(get_current_user),
):
    """Execute a lifecycle transition — the core workflow."""
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    updated_asset = await execute_transition(
        asset=asset,
        to_stage=data.to_stage,
        performed_by=current_user.username,
        notes=data.notes,
        metadata=data.metadata,
    )

    return {
        "asset": _asset_to_dict(updated_asset),
        "message": f"Transitioned from {asset.previous_stage} to {updated_asset.current_stage}",
    }


@router.get("/{asset_id}/timeline")
async def get_asset_timeline(asset_id: str, current_user: User = Depends(get_current_user)):
    """Get complete lifecycle timeline for an asset."""
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    events = await get_lifecycle_timeline(asset.id)

    # Also include inspections, maintenance, and condition assessments in timeline
    inspections = await Inspection.find(Inspection.asset_id == asset.id).sort("-inspection_date").to_list()
    maintenance = await MaintenanceRecord.find(MaintenanceRecord.asset_id == asset.id).sort("-created_at").to_list()
    conditions = await ConditionAssessment.find(ConditionAssessment.asset_id == asset.id).sort("-assessment_date").to_list()

    timeline = []

    for e in events:
        timeline.append({
            "type": "lifecycle",
            "date": e["transition_date"],
            "title": f"Lifecycle: {e['from_stage']} → {e['to_stage']}",
            "description": e["notes"],
            "performed_by": e["performed_by"],
        })

    for insp in inspections:
        timeline.append({
            "type": "inspection",
            "date": insp.inspection_date.isoformat(),
            "title": f"Inspection: {insp.inspection_type}",
            "description": insp.findings[:200] if insp.findings else "",
            "performed_by": insp.inspector_name,
            "condition": insp.overall_condition,
            "score": insp.condition_score,
        })

    for m in maintenance:
        timeline.append({
            "type": "maintenance",
            "date": m.created_at.isoformat(),
            "title": f"Maintenance: {m.maintenance_type} — {m.title}",
            "description": m.description[:200] if m.description else "",
            "status": m.status,
            "priority": m.priority,
        })

    for c in conditions:
        timeline.append({
            "type": "condition",
            "date": c.assessment_date.isoformat(),
            "title": f"Condition Assessment: {c.overall_rating} ({c.overall_score}/100)",
            "description": c.findings[:200] if c.findings else "",
            "performed_by": c.inspector,
            "score": c.overall_score,
            "rating": c.overall_rating,
        })

    # Sort by date descending
    timeline.sort(key=lambda x: x["date"], reverse=True)

    return {"timeline": timeline, "total": len(timeline)}


# ── Components, Documents, Costs ─────────────────────────────────────────────

@router.get("/{asset_id}/components")
async def list_components(asset_id: str, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    components = await AssetComponent.find(AssetComponent.asset_id == asset.id).to_list()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "component_type": c.component_type,
            "description": c.description,
            "condition": c.condition,
            "condition_score": c.condition_score,
            "is_critical": c.is_critical,
            "installed_date": c.installed_date.isoformat() if c.installed_date else None,
            "warranty_expiry": c.warranty_expiry.isoformat() if c.warranty_expiry else None,
        }
        for c in components
    ]


@router.post("/{asset_id}/components", status_code=status.HTTP_201_CREATED)
async def create_component(asset_id: str, data: dict, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    comp = AssetComponent(asset_id=asset.id, **data)
    await comp.insert()
    return {"id": str(comp.id), "name": comp.name, "message": "Component created"}


@router.get("/{asset_id}/documents")
async def list_documents(asset_id: str, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    docs = await AssetDocument.find(AssetDocument.asset_id == asset.id).to_list()
    return [
        {
            "id": str(d.id),
            "title": d.title,
            "document_type": d.document_type,
            "description": d.description,
            "file_name": d.file_name,
            "file_url": d.file_url,
            "uploaded_by": d.uploaded_by,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@router.post("/{asset_id}/documents", status_code=status.HTTP_201_CREATED)
async def create_document(asset_id: str, data: dict, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    doc = AssetDocument(asset_id=asset.id, **data)
    await doc.insert()
    return {"id": str(doc.id), "title": doc.title, "message": "Document created"}


@router.get("/{asset_id}/costs")
async def list_costs(asset_id: str, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    costs = await AssetCost.find(AssetCost.asset_id == asset.id).sort("-created_at").to_list()
    total_by_type = {}
    result = []
    for c in costs:
        total_by_type[c.cost_type] = total_by_type.get(c.cost_type, 0) + c.amount
        result.append({
            "id": str(c.id),
            "cost_type": c.cost_type,
            "description": c.description,
            "amount": c.amount,
            "financial_year": c.financial_year,
            "date_incurred": c.date_incurred.isoformat() if c.date_incurred else None,
            "source_of_funds": c.source_of_funds,
            "created_at": c.created_at.isoformat(),
        })
    return {
        "items": result,
        "total_by_type": total_by_type,
        "grand_total": sum(total_by_type.values()),
    }


@router.post("/{asset_id}/costs", status_code=status.HTTP_201_CREATED)
async def create_cost(asset_id: str, data: dict, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    cost = AssetCost(asset_id=asset.id, **data)
    await cost.insert()
    return {"id": str(cost.id), "message": "Cost record created"}


# ── Helper ───────────────────────────────────────────────────────────────────

def _asset_to_dict(a: Asset) -> dict:
    return {
        "id": str(a.id),
        "code": a.code,
        "name": a.name,
        "description": a.description,
        "infrastructure_class_id": str(a.infrastructure_class_id),
        "infrastructure_class_code": a.infrastructure_class_code,
        "asset_type_id": str(a.asset_type_id),
        "asset_type_name": a.asset_type_name,
        "project_id": str(a.project_id) if a.project_id else None,
        "project_code": a.project_code,
        "lifecycle_template_id": str(a.lifecycle_template_id) if a.lifecycle_template_id else None,
        "current_stage": a.current_stage,
        "previous_stage": a.previous_stage,
        "location": a.location.model_dump() if a.location else {},
        "commissioned_date": a.commissioned_date.isoformat() if a.commissioned_date else None,
        "handover_date": a.handover_date.isoformat() if a.handover_date else None,
        "responsibility": a.responsibility.model_dump() if a.responsibility else {},
        "current_condition_score": a.current_condition_score,
        "current_condition_rating": a.current_condition_rating,
        "performance_metrics": a.performance_metrics,
        "current_risk_level": a.current_risk_level,
        "risk_score": a.risk_score,
        "next_action": a.next_action,
        "next_action_due": a.next_action_due.isoformat() if a.next_action_due else None,
        "next_action_priority": a.next_action_priority,
        "last_inspection_date": a.last_inspection_date.isoformat() if a.last_inspection_date else None,
        "next_inspection_due": a.next_inspection_due.isoformat() if a.next_inspection_due else None,
        "estimated_value": a.estimated_value,
        "replacement_value": a.replacement_value,
        "planned_lifecycle": a.planned_lifecycle.model_dump() if a.planned_lifecycle else {},
        "metadata": a.metadata,
        "is_active": a.is_active,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),
    }
