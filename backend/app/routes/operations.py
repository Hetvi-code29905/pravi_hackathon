"""
Operations Routes — Inspections, Condition Assessments, Maintenance Records, Issues & Risk.
This connects condition monitoring, field inspections, maintenance execution, and risk assessment.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date
from beanie import PydanticObjectId

from app.models.asset import Asset
from app.models.inspection import Inspection
from app.models.condition import ConditionAssessment
from app.models.maintenance import MaintenanceRecord
from app.models.issue import Issue
from app.models.risk import RiskAssessment
from app.services.risk_engine import assess_risk_for_asset, compute_overall_risk, calculate_risk_level
from app.services.lifecycle_engine import calculate_next_action
from app.auth.utils import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/api", tags=["Operations"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class InspectionCreate(BaseModel):
    inspection_type: str = Field(default="ROUTINE", description="ROUTINE | INITIAL | SPECIAL | EMERGENCY | PERIODIC")
    inspection_date: date
    inspector_name: str
    inspector_designation: str = ""
    inspector_agency: str = "Gujarat R&B Quality Control Wing"
    overall_condition: str = Field(default="GOOD", description="GOOD | FAIR | POOR | CRITICAL")
    condition_score: Optional[float] = Field(default=None, ge=0, le=100)
    structural_condition: str = "GOOD"
    functional_condition: str = "GOOD"
    safety_condition: str = "GOOD"
    findings: str = ""
    recommendations: str = ""
    defects_found: List[str] = Field(default_factory=list)
    next_inspection_date: Optional[date] = None
    requires_immediate_action: bool = False
    immediate_action_description: str = ""
    photographs: List[str] = Field(default_factory=list)


class ConditionAssessmentCreate(BaseModel):
    assessment_date: date
    overall_score: float = Field(..., ge=0, le=100)
    overall_rating: str = Field(..., description="GOOD | FAIR | POOR | CRITICAL")
    structural_condition: str = "GOOD"
    structural_score: Optional[float] = None
    functional_condition: str = "GOOD"
    functional_score: Optional[float] = None
    safety_condition: str = "GOOD"
    safety_score: Optional[float] = None
    inspector: str = ""
    findings: str = ""
    recommendations: str = ""
    performance_data: Dict = Field(default_factory=dict)


class MaintenanceCreate(BaseModel):
    maintenance_type: str = Field(..., description="ROUTINE | PREVENTIVE | CORRECTIVE | REPAIR | REHABILITATION | RENEWAL | RECONSTRUCTION")
    title: str
    description: str = ""
    priority: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | URGENT")
    estimated_cost: float = 0.0
    scheduled_date: Optional[date] = None
    assigned_agency: str = ""
    triggered_by_inspection_id: Optional[str] = None
    triggered_by_condition: Optional[str] = None


class MaintenanceUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    actual_cost: Optional[float] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    assigned_agency: Optional[str] = None
    performed_by: Optional[str] = None
    approved_by: Optional[str] = None
    work_done: Optional[str] = None
    notes: Optional[str] = None
    condition_after: Optional[str] = None


class IssueCreate(BaseModel):
    title: str
    description: str = ""
    severity: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | CRITICAL")
    category: str = "STRUCTURAL"
    reported_by: str = ""


class IssueUpdate(BaseModel):
    status: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None


class RiskAssessRequest(BaseModel):
    criticality: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | CRITICAL")
    safety_impact: str = Field(default="LOW", description="LOW | MEDIUM | HIGH | CRITICAL")
    service_impact: str = Field(default="LOW", description="LOW | MEDIUM | HIGH | CRITICAL")


# ── Inspection Endpoints ─────────────────────────────────────────────────────

@router.get("/inspections")
async def list_all_inspections(
    asset_id: Optional[str] = None,
    inspection_type: Optional[str] = None,
    overall_condition: Optional[str] = None,
    requires_immediate_action: Optional[bool] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    current_user: User = Depends(get_current_user),
):
    query = {}
    if asset_id:
        query["asset_id"] = PydanticObjectId(asset_id)
    if inspection_type:
        query["inspection_type"] = inspection_type
    if overall_condition:
        query["overall_condition"] = overall_condition
    if requires_immediate_action is not None:
        query["requires_immediate_action"] = requires_immediate_action

    items = await Inspection.find(query).sort("-inspection_date").skip(skip).limit(limit).to_list()
    total = await Inspection.find(query).count()

    results = []
    for insp in items:
        asset = await Asset.get(insp.asset_id)
        results.append({
            "id": str(insp.id),
            "asset_id": str(insp.asset_id),
            "asset_name": asset.name if asset else "Unknown Asset",
            "asset_code": asset.code if asset else "",
            "infrastructure_class_code": asset.infrastructure_class_code if asset else "",
            "inspection_type": insp.inspection_type,
            "inspection_date": insp.inspection_date.isoformat(),
            "inspector_name": insp.inspector_name,
            "inspector_designation": insp.inspector_designation,
            "inspector_agency": insp.inspector_agency,
            "overall_condition": insp.overall_condition,
            "condition_score": insp.condition_score,
            "structural_condition": insp.structural_condition,
            "functional_condition": insp.functional_condition,
            "safety_condition": insp.safety_condition,
            "findings": insp.findings,
            "recommendations": insp.recommendations,
            "defects_found": insp.defects_found,
            "next_inspection_date": insp.next_inspection_date.isoformat() if insp.next_inspection_date else None,
            "requires_immediate_action": insp.requires_immediate_action,
            "immediate_action_description": insp.immediate_action_description,
            "photographs": insp.photographs,
            "created_at": insp.created_at.isoformat(),
        })

    return {"items": results, "total": total, "skip": skip, "limit": limit}


@router.get("/assets/{asset_id}/inspections")
async def list_asset_inspections(asset_id: str, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    items = await Inspection.find(Inspection.asset_id == asset.id).sort("-inspection_date").to_list()
    return [
        {
            "id": str(insp.id),
            "asset_id": str(insp.asset_id),
            "inspection_type": insp.inspection_type,
            "inspection_date": insp.inspection_date.isoformat(),
            "inspector_name": insp.inspector_name,
            "inspector_designation": insp.inspector_designation,
            "inspector_agency": insp.inspector_agency,
            "overall_condition": insp.overall_condition,
            "condition_score": insp.condition_score,
            "structural_condition": insp.structural_condition,
            "functional_condition": insp.functional_condition,
            "safety_condition": insp.safety_condition,
            "findings": insp.findings,
            "recommendations": insp.recommendations,
            "defects_found": insp.defects_found,
            "next_inspection_date": insp.next_inspection_date.isoformat() if insp.next_inspection_date else None,
            "requires_immediate_action": insp.requires_immediate_action,
            "immediate_action_description": insp.immediate_action_description,
            "photographs": insp.photographs,
            "created_at": insp.created_at.isoformat(),
        }
        for insp in items
    ]


@router.post("/assets/{asset_id}/inspections", status_code=status.HTTP_201_CREATED)
async def create_asset_inspection(
    asset_id: str,
    data: InspectionCreate,
    current_user: User = Depends(get_current_user),
):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    inspection = Inspection(
        asset_id=asset.id,
        inspection_type=data.inspection_type,
        inspection_date=data.inspection_date,
        inspector_name=data.inspector_name,
        inspector_designation=data.inspector_designation,
        inspector_agency=data.inspector_agency,
        overall_condition=data.overall_condition,
        condition_score=data.condition_score,
        structural_condition=data.structural_condition,
        functional_condition=data.functional_condition,
        safety_condition=data.safety_condition,
        findings=data.findings,
        recommendations=data.recommendations,
        defects_found=data.defects_found,
        next_inspection_date=data.next_inspection_date,
        requires_immediate_action=data.requires_immediate_action,
        immediate_action_description=data.immediate_action_description,
        photographs=data.photographs,
    )
    await inspection.insert()

    # Update asset state from inspection
    asset.last_inspection_date = data.inspection_date
    if data.next_inspection_date:
        asset.next_inspection_due = data.next_inspection_date
    if data.condition_score is not None:
        asset.current_condition_score = data.condition_score
    if data.overall_condition:
        asset.current_condition_rating = data.overall_condition

    # Recompute risk & next action
    await calculate_next_action(asset)
    asset.updated_at = datetime.utcnow()
    await asset.save()

    return {"id": str(inspection.id), "message": "Inspection recorded successfully", "asset_id": str(asset.id)}


# ── Condition Assessment Endpoints ───────────────────────────────────────────

@router.get("/assets/{asset_id}/conditions")
async def list_asset_conditions(asset_id: str, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    records = await ConditionAssessment.find(ConditionAssessment.asset_id == asset.id).sort("-assessment_date").to_list()
    return [
        {
            "id": str(c.id),
            "asset_id": str(c.asset_id),
            "assessment_date": c.assessment_date.isoformat(),
            "overall_score": c.overall_score,
            "overall_rating": c.overall_rating,
            "structural_condition": c.structural_condition,
            "structural_score": c.structural_score,
            "functional_condition": c.functional_condition,
            "functional_score": c.functional_score,
            "safety_condition": c.safety_condition,
            "safety_score": c.safety_score,
            "inspector": c.inspector,
            "findings": c.findings,
            "recommendations": c.recommendations,
            "performance_data": c.performance_data,
            "created_at": c.created_at.isoformat(),
        }
        for c in records
    ]


@router.post("/assets/{asset_id}/conditions", status_code=status.HTTP_201_CREATED)
async def create_asset_condition(
    asset_id: str,
    data: ConditionAssessmentCreate,
    current_user: User = Depends(get_current_user),
):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    assessment = ConditionAssessment(
        asset_id=asset.id,
        assessment_date=data.assessment_date,
        overall_score=data.overall_score,
        overall_rating=data.overall_rating,
        structural_condition=data.structural_condition,
        structural_score=data.structural_score,
        functional_condition=data.functional_condition,
        functional_score=data.functional_score,
        safety_condition=data.safety_condition,
        safety_score=data.safety_score,
        inspector=data.inspector,
        findings=data.findings,
        recommendations=data.recommendations,
        performance_data=data.performance_data,
    )
    await assessment.insert()

    # Update asset condition fields
    asset.current_condition_score = data.overall_score
    asset.current_condition_rating = data.overall_rating
    await calculate_next_action(asset)
    asset.updated_at = datetime.utcnow()
    await asset.save()

    return {"id": str(assessment.id), "message": "Condition assessment recorded", "overall_rating": data.overall_rating}


# ── Maintenance Endpoints ────────────────────────────────────────────────────

@router.get("/maintenance")
async def list_all_maintenance(
    asset_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    maintenance_type: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    current_user: User = Depends(get_current_user),
):
    query = {}
    if asset_id:
        query["asset_id"] = PydanticObjectId(asset_id)
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if maintenance_type:
        query["maintenance_type"] = maintenance_type

    items = await MaintenanceRecord.find(query).sort("-created_at").skip(skip).limit(limit).to_list()
    total = await MaintenanceRecord.find(query).count()

    results = []
    for m in items:
        asset = await Asset.get(m.asset_id)
        results.append({
            "id": str(m.id),
            "asset_id": str(m.asset_id),
            "asset_name": asset.name if asset else "Unknown Asset",
            "asset_code": asset.code if asset else "",
            "infrastructure_class_code": asset.infrastructure_class_code if asset else "",
            "maintenance_type": m.maintenance_type,
            "title": m.title,
            "description": m.description,
            "priority": m.priority,
            "status": m.status,
            "estimated_cost": m.estimated_cost,
            "actual_cost": m.actual_cost,
            "scheduled_date": m.scheduled_date.isoformat() if m.scheduled_date else None,
            "start_date": m.start_date.isoformat() if m.start_date else None,
            "completion_date": m.completion_date.isoformat() if m.completion_date else None,
            "assigned_agency": m.assigned_agency,
            "performed_by": m.performed_by,
            "approved_by": m.approved_by,
            "work_done": m.work_done,
            "notes": m.notes,
            "condition_after": m.condition_after,
            "created_at": m.created_at.isoformat(),
        })

    return {"items": results, "total": total, "skip": skip, "limit": limit}


@router.get("/assets/{asset_id}/maintenance")
async def list_asset_maintenance(asset_id: str, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    items = await MaintenanceRecord.find(MaintenanceRecord.asset_id == asset.id).sort("-created_at").to_list()
    return [
        {
            "id": str(m.id),
            "maintenance_type": m.maintenance_type,
            "title": m.title,
            "description": m.description,
            "priority": m.priority,
            "status": m.status,
            "estimated_cost": m.estimated_cost,
            "actual_cost": m.actual_cost,
            "scheduled_date": m.scheduled_date.isoformat() if m.scheduled_date else None,
            "start_date": m.start_date.isoformat() if m.start_date else None,
            "completion_date": m.completion_date.isoformat() if m.completion_date else None,
            "assigned_agency": m.assigned_agency,
            "performed_by": m.performed_by,
            "approved_by": m.approved_by,
            "work_done": m.work_done,
            "notes": m.notes,
            "condition_after": m.condition_after,
            "created_at": m.created_at.isoformat(),
        }
        for m in items
    ]


@router.post("/assets/{asset_id}/maintenance", status_code=status.HTTP_201_CREATED)
async def create_asset_maintenance(
    asset_id: str,
    data: MaintenanceCreate,
    current_user: User = Depends(get_current_user),
):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    rec = MaintenanceRecord(
        asset_id=asset.id,
        maintenance_type=data.maintenance_type,
        title=data.title,
        description=data.description,
        priority=data.priority,
        estimated_cost=data.estimated_cost,
        scheduled_date=data.scheduled_date,
        assigned_agency=data.assigned_agency or asset.responsibility.maintenance_agency,
        triggered_by_inspection_id=PydanticObjectId(data.triggered_by_inspection_id) if data.triggered_by_inspection_id else None,
        triggered_by_condition=data.triggered_by_condition,
    )
    await rec.insert()
    return {"id": str(rec.id), "title": rec.title, "message": "Maintenance task scheduled"}


@router.patch("/maintenance/{maintenance_id}")
async def update_maintenance(
    maintenance_id: str,
    data: MaintenanceUpdate,
    current_user: User = Depends(get_current_user),
):
    rec = await MaintenanceRecord.get(PydanticObjectId(maintenance_id))
    if not rec:
        raise HTTPException(status_code=404, detail="Maintenance record not found")

    update_dict = data.model_dump(exclude_none=True)
    for k, v in update_dict.items():
        setattr(rec, k, v)

    rec.updated_at = datetime.utcnow()
    await rec.save()

    # If completed and condition_after is given, update asset condition
    if rec.status == "COMPLETED" and rec.condition_after:
        asset = await Asset.get(rec.asset_id)
        if asset:
            score_map = {"EXCELLENT": 95, "GOOD": 80, "FAIR": 60, "POOR": 40}
            asset.current_condition_rating = rec.condition_after
            if rec.condition_after in score_map:
                asset.current_condition_score = score_map[rec.condition_after]
            await recalculate_next_action(asset)
            asset.updated_at = datetime.utcnow()
            await asset.save()

    return {"id": str(rec.id), "status": rec.status, "message": "Maintenance record updated"}


# ── Issues Endpoints ─────────────────────────────────────────────────────────

@router.get("/issues")
async def list_all_issues(
    asset_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    current_user: User = Depends(get_current_user),
):
    query = {}
    if asset_id:
        query["asset_id"] = PydanticObjectId(asset_id)
    if status:
        query["status"] = status
    if severity:
        query["severity"] = severity

    items = await Issue.find(query).sort("-created_at").skip(skip).limit(limit).to_list()
    total = await Issue.find(query).count()

    results = []
    for issue in items:
        asset = await Asset.get(issue.asset_id)
        results.append({
            "id": str(issue.id),
            "asset_id": str(issue.asset_id),
            "asset_name": asset.name if asset else "Unknown Asset",
            "asset_code": asset.code if asset else "",
            "title": issue.title,
            "description": issue.description,
            "severity": issue.severity,
            "category": issue.category,
            "status": issue.status,
            "reported_by": issue.reported_by,
            "assigned_to": issue.assigned_to,
            "resolution_notes": getattr(issue, "resolution_notes", None) or getattr(issue, "resolution", ""),
            "created_at": issue.created_at.isoformat() if issue.created_at else "",
            "resolved_at": (
                issue.resolved_at.isoformat()
                if getattr(issue, "resolved_at", None)
                else (issue.resolved_date.isoformat() if getattr(issue, "resolved_date", None) else None)
            ),
        })
    return {"items": results, "total": total, "skip": skip, "limit": limit}


@router.get("/assets/{asset_id}/issues")
async def list_asset_issues(asset_id: str, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    items = await Issue.find(Issue.asset_id == asset.id).sort("-created_at").to_list()
    return [
        {
            "id": str(issue.id),
            "title": issue.title,
            "description": issue.description,
            "severity": issue.severity,
            "category": issue.category,
            "status": issue.status,
            "reported_by": issue.reported_by,
            "assigned_to": issue.assigned_to,
            "resolution_notes": getattr(issue, "resolution_notes", None) or getattr(issue, "resolution", ""),
            "created_at": issue.created_at.isoformat() if issue.created_at else "",
            "resolved_at": (
                issue.resolved_at.isoformat()
                if getattr(issue, "resolved_at", None)
                else (issue.resolved_date.isoformat() if getattr(issue, "resolved_date", None) else None)
            ),
        }
        for issue in items
    ]


@router.post("/assets/{asset_id}/issues", status_code=status.HTTP_201_CREATED)
async def create_asset_issue(
    asset_id: str,
    data: IssueCreate,
    current_user: User = Depends(get_current_user),
):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    issue = Issue(
        asset_id=asset.id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        category=data.category,
        reported_by=data.reported_by or current_user.username,
        status="OPEN",
    )
    await issue.insert()
    return {"id": str(issue.id), "title": issue.title, "message": "Issue recorded"}


@router.patch("/issues/{issue_id}")
async def update_issue(
    issue_id: str,
    data: IssueUpdate,
    current_user: User = Depends(get_current_user),
):
    issue = await Issue.get(PydanticObjectId(issue_id))
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    update_dict = data.model_dump(exclude_none=True)
    for k, v in update_dict.items():
        setattr(issue, k, v)

    if issue.status == "RESOLVED" and not issue.resolved_at:
        issue.resolved_at = datetime.utcnow()

    await issue.save()
    return {"id": str(issue.id), "status": issue.status, "message": "Issue updated"}


# ── Risk Assessment Endpoints ────────────────────────────────────────────────

@router.post("/assets/{asset_id}/risk/assess")
async def trigger_asset_risk_assessment(
    asset_id: str,
    data: RiskAssessRequest,
    current_user: User = Depends(get_current_user),
):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    assessment = await assess_risk_for_asset(
        asset=asset,
        criticality=data.criticality,
        safety_impact=data.safety_impact,
        service_impact=data.service_impact,
    )

    return {
        "id": str(assessment.id),
        "overall_risk": assessment.overall_risk,
        "risk_score": assessment.risk_score,
        "probability": assessment.probability,
        "consequence": assessment.consequence,
        "recommendations": assessment.recommendations,
        "mitigation_actions": assessment.mitigation_actions,
        "factors": assessment.factors,
        "message": f"Asset risk evaluated: {assessment.overall_risk} ({assessment.risk_score})",
    }


@router.get("/assets/{asset_id}/risk/history")
async def get_asset_risk_history(asset_id: str, current_user: User = Depends(get_current_user)):
    asset = await Asset.get(PydanticObjectId(asset_id))
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    items = await RiskAssessment.find(RiskAssessment.asset_id == asset.id).sort("-assessment_date").to_list()
    return [
        {
            "id": str(r.id),
            "assessment_date": r.assessment_date.isoformat(),
            "condition_score": r.condition_score,
            "condition_rating": r.condition_rating,
            "criticality": r.criticality,
            "overall_risk": r.overall_risk,
            "risk_score": r.risk_score,
            "probability": r.probability,
            "consequence": r.consequence,
            "recommendations": r.recommendations,
            "mitigation_actions": r.mitigation_actions,
            "factors": r.factors,
            "created_at": r.created_at.isoformat(),
        }
        for r in items
    ]
