"""Project routes — the temporary lifecycle from NEED to CLOSED."""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from beanie import PydanticObjectId

from app.models.project import Project, ProjectLocation
from app.models.infrastructure import InfrastructureClass
from app.models.asset_type import AssetType
from app.models.asset import Asset, AssetLocation, AssetResponsibility, PlannedLifecycle
from app.models.lifecycle import LifecycleTemplate, LifecycleEvent
from app.auth.utils import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/api/projects", tags=["Projects"])

PROJECT_STATUSES = [
    "NEED", "PLANNING", "DESIGN", "TENDER", "CONSTRUCTION",
    "QUALITY_ACCEPTANCE", "COMMISSIONING", "HANDOVER", "CLOSED",
]


# ── Schemas ──────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    infrastructure_class_id: str
    asset_type_id: str
    location: Optional[dict] = None
    estimated_cost: float = 0.0
    sanctioned_cost: float = 0.0
    start_date: Optional[date] = None
    expected_completion: Optional[date] = None
    contractor: str = ""
    supervising_officer: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    location: Optional[dict] = None
    estimated_cost: Optional[float] = None
    sanctioned_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    start_date: Optional[date] = None
    expected_completion: Optional[date] = None
    actual_completion: Optional[date] = None
    contractor: Optional[str] = None
    supervising_officer: Optional[str] = None


class CreateAssetFromProject(BaseModel):
    """Create a physical asset when project reaches handover."""
    name: str
    description: str = ""
    custodian: str = "Roads & Buildings Department"
    operator: str = ""
    maintenance_agency: str = ""
    estimated_value: float = 0.0
    commissioned_date: Optional[date] = None
    metadata: dict = {}


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("")
async def list_projects(
    status: Optional[str] = None,
    infrastructure_class_code: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=100),
    current_user: User = Depends(get_current_user),
):
    """List all projects with optional filters."""
    query = {}
    if status:
        query["status"] = status
    if infrastructure_class_code:
        query["infrastructure_class_code"] = infrastructure_class_code

    projects = await Project.find(query).skip(skip).limit(limit).sort("-created_at").to_list()
    total = await Project.find(query).count()

    return {
        "items": [_project_to_dict(p) for p in projects],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{project_id}")
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Get project details."""
    project = await Project.get(PydanticObjectId(project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_to_dict(project)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, current_user: User = Depends(get_current_user)):
    """Create a new project."""
    # Validate infrastructure class
    infra_class = await InfrastructureClass.get(PydanticObjectId(data.infrastructure_class_id))
    if not infra_class:
        raise HTTPException(status_code=400, detail="Invalid infrastructure class")

    # Validate asset type
    asset_type = await AssetType.get(PydanticObjectId(data.asset_type_id))
    if not asset_type:
        raise HTTPException(status_code=400, detail="Invalid asset type")

    # Generate project code
    count = await Project.find().count()
    year = datetime.now().year
    code = f"PRJ-RNB-{year}-{str(count + 1).zfill(4)}"

    location = ProjectLocation(**(data.location or {}))

    project = Project(
        code=code,
        name=data.name,
        description=data.description,
        infrastructure_class_id=infra_class.id,
        infrastructure_class_code=infra_class.code,
        asset_type_id=asset_type.id,
        asset_type_name=asset_type.name,
        status="NEED",
        location=location,
        estimated_cost=data.estimated_cost,
        sanctioned_cost=data.sanctioned_cost,
        start_date=data.start_date,
        expected_completion=data.expected_completion,
        contractor=data.contractor,
        supervising_officer=data.supervising_officer,
        created_by=current_user.username,
    )
    await project.insert()
    return _project_to_dict(project)


@router.patch("/{project_id}")
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a project."""
    project = await Project.get(PydanticObjectId(project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = data.model_dump(exclude_none=True)

    # Handle location
    if "location" in update_data:
        update_data["location"] = ProjectLocation(**update_data["location"])

    # Validate status transition
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status not in PROJECT_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

    for key, value in update_data.items():
        setattr(project, key, value)

    project.updated_at = datetime.utcnow()
    await project.save()
    return _project_to_dict(project)


@router.post("/{project_id}/create-asset", status_code=status.HTTP_201_CREATED)
async def create_asset_from_project(
    project_id: str,
    data: CreateAssetFromProject,
    current_user: User = Depends(get_current_user),
):
    """
    Create a physical asset from a project.
    This is the critical workflow: Project → Asset Passport.
    """
    project = await Project.get(PydanticObjectId(project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.asset_id:
        raise HTTPException(status_code=400, detail="Project already has a linked asset")

    # Find lifecycle template
    template = await LifecycleTemplate.find_one(
        LifecycleTemplate.infrastructure_class_code == project.infrastructure_class_code,
        LifecycleTemplate.is_active == True,
    )

    # Generate asset code
    prefix_map = {"BUILDING": "BLD", "ROAD": "RD", "BRIDGE": "BRG"}
    prefix = prefix_map.get(project.infrastructure_class_code, "AST")
    count = await Asset.find(
        Asset.infrastructure_class_code == project.infrastructure_class_code
    ).count()
    asset_code = f"R&B-{prefix}-{str(count + 1).zfill(5)}"

    # Create the physical asset
    asset = Asset(
        code=asset_code,
        name=data.name,
        description=data.description,
        infrastructure_class_id=project.infrastructure_class_id,
        infrastructure_class_code=project.infrastructure_class_code,
        asset_type_id=project.asset_type_id,
        asset_type_name=project.asset_type_name,
        project_id=project.id,
        project_code=project.code,
        lifecycle_template_id=template.id if template else None,
        current_stage="COMMISSIONED" if data.commissioned_date else "CREATED",
        location=AssetLocation(
            district=project.location.district,
            taluka=project.location.taluka,
            city=project.location.city,
            address=project.location.address,
            pin_code=project.location.pin_code,
            latitude=project.location.latitude,
            longitude=project.location.longitude,
        ),
        commissioned_date=data.commissioned_date,
        responsibility=AssetResponsibility(
            custodian=data.custodian,
            operator=data.operator,
            maintenance_agency=data.maintenance_agency,
        ),
        estimated_value=data.estimated_value or project.actual_cost or project.estimated_cost,
        current_condition_score=100.0,
        current_condition_rating="GOOD",
        current_risk_level="LOW",
        next_action="Complete handover and prepare asset passport",
        next_action_priority="HIGH",
        metadata=data.metadata,
        planned_lifecycle=PlannedLifecycle(),
    )
    await asset.insert()

    # Create initial lifecycle event
    event = LifecycleEvent(
        asset_id=asset.id,
        from_stage="PROJECT",
        to_stage=asset.current_stage,
        performed_by=current_user.username,
        notes=f"Asset created from project {project.code}",
        metadata={"project_id": str(project.id), "project_code": project.code},
    )
    await event.insert()

    # Update project with linked asset
    project.asset_id = asset.id
    project.status = "HANDOVER"
    project.updated_at = datetime.utcnow()
    await project.save()

    return {
        "project": _project_to_dict(project),
        "asset": {
            "id": str(asset.id),
            "code": asset.code,
            "name": asset.name,
            "current_stage": asset.current_stage,
        },
        "message": f"Asset {asset_code} created from project {project.code}",
    }


class ProjectReviewRequest(BaseModel):
    action_type: str = Field(..., description="CLEARANCE_REVIEW | MILESTONE_INSPECTION | HANDOVER_SANCTION | REHAB_SANCTION")
    decision: str = Field(..., description="ACCEPTED | REJECTED")
    remarks: Optional[str] = ""
    target_stage: Optional[str] = None


@router.post("/{project_id}/review")
async def review_project_lifecycle(
    project_id: str,
    data: ProjectReviewRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Role-gated actionable review: Accepts or Rejects a clearance, milestone, or handover sanction,
    directly advancing the project lifecycle in MongoDB.
    """
    project = await Project.get(PydanticObjectId(project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user_role = (current_user.role or "").upper()
    decision = data.decision.upper()
    action_type = data.action_type.upper()

    # ── Role Authority Matrix ────────────────────────────────────────────────
    if action_type in ["CLEARANCE_REVIEW", "HANDOVER_SANCTION", "REHAB_SANCTION"]:
        if user_role not in ["SECRETARY", "ADMIN", "ENGINEER"]:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user_role}' lacks authority for {action_type}. Requires SECRETARY, ADMIN, or Executive ENGINEER."
            )
    elif action_type == "MILESTONE_INSPECTION":
        if user_role not in ["ENGINEER", "INSPECTOR", "ADMIN"]:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user_role}' lacks authority for MILESTONE_INSPECTION. Requires ENGINEER, INSPECTOR, or ADMIN."
            )

    old_status = project.status
    new_status = old_status
    created_asset = None

    if decision == "ACCEPTED":
        if action_type == "CLEARANCE_REVIEW":
            if project.status in ["NEED", "PLANNING"]:
                new_status = "DESIGN"
            elif project.status == "DESIGN":
                new_status = "TENDER"
            elif project.status == "TENDER":
                new_status = "CONSTRUCTION"

        elif action_type == "MILESTONE_INSPECTION":
            if project.status == "CONSTRUCTION":
                new_status = "QUALITY_ACCEPTANCE"
            elif project.status == "QUALITY_ACCEPTANCE":
                new_status = "COMMISSIONING"

        elif action_type == "HANDOVER_SANCTION":
            new_status = "HANDOVER"
            # Auto create asset if not already created
            if not project.asset_id:
                prefix_map = {"BUILDING": "BLD", "ROAD": "RD", "BRIDGE": "BRG"}
                prefix = prefix_map.get(project.infrastructure_class_code, "AST")
                count = await Asset.find(
                    Asset.infrastructure_class_code == project.infrastructure_class_code
                ).count()
                asset_code = f"R&B-{prefix}-{str(count + 1).zfill(5)}"
                template = await LifecycleTemplate.find_one(
                    LifecycleTemplate.infrastructure_class_code == project.infrastructure_class_code,
                    LifecycleTemplate.is_active == True,
                )

                asset = Asset(
                    code=asset_code,
                    name=project.name,
                    description=project.description or f"Commissioned infrastructure asset from {project.code}",
                    infrastructure_class_id=project.infrastructure_class_id,
                    infrastructure_class_code=project.infrastructure_class_code,
                    asset_type_id=project.asset_type_id,
                    asset_type_name=project.asset_type_name,
                    project_id=project.id,
                    project_code=project.code,
                    lifecycle_template_id=template.id if template else None,
                    current_stage="OPERATIONAL",
                    location=AssetLocation(
                        district=project.location.district,
                        taluka=project.location.taluka,
                        city=project.location.city,
                        address=project.location.address,
                        pin_code=project.location.pin_code,
                        latitude=project.location.latitude,
                        longitude=project.location.longitude,
                    ) if project.location else AssetLocation(),
                    responsibility=AssetResponsibility(
                        custodian="Roads & Buildings Department",
                        operator="Gujarat State Authority",
                        maintenance_agency="R&B Division",
                    ),
                    estimated_value=project.sanctioned_cost or project.estimated_cost or 5000.0,
                    current_condition_score=95.0,
                    current_condition_rating="EXCELLENT",
                    current_risk_level="LOW",
                    next_action="Routine 180-day structural inspection",
                    next_action_priority="LOW",
                    planned_lifecycle=PlannedLifecycle(),
                )
                await asset.insert()
                project.asset_id = asset.id
                created_asset = {
                    "id": str(asset.id),
                    "code": asset.code,
                    "name": asset.name,
                    "current_stage": asset.current_stage,
                }

        elif action_type == "REHAB_SANCTION":
            new_status = "CONSTRUCTION"

    # Save changes to project
    project.status = new_status
    project.updated_at = datetime.utcnow()
    await project.save()

    return {
        "success": True,
        "action_type": action_type,
        "decision": decision,
        "old_status": old_status,
        "new_status": new_status,
        "remarks": data.remarks,
        "reviewed_by": current_user.full_name or current_user.username,
        "role": user_role,
        "project": _project_to_dict(project),
        "created_asset": created_asset,
    }


class ProjectAdvanceRequest(BaseModel):
    target_status: Optional[str] = None
    remarks: Optional[str] = ""


@router.post("/{project_id}/advance")
async def advance_project_stage(
    project_id: str,
    data: ProjectAdvanceRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Advance a project sequentially through lifecycle stages.
    """
    project = await Project.get(PydanticObjectId(project_id))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    user_role = (current_user.role or "").upper()
    if user_role not in ["SECRETARY", "ADMIN", "ENGINEER"]:
        raise HTTPException(status_code=403, detail="Only Engineers, Administrators, and Secretaries can advance project stages.")

    current_idx = PROJECT_STATUSES.index(project.status) if project.status in PROJECT_STATUSES else 0
    if data.target_status:
        if data.target_status not in PROJECT_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid target status: {data.target_status}")
        new_status = data.target_status
    else:
        if current_idx < len(PROJECT_STATUSES) - 1:
            new_status = PROJECT_STATUSES[current_idx + 1]
        else:
            new_status = project.status

    old_status = project.status
    project.status = new_status
    project.updated_at = datetime.utcnow()
    await project.save()

    return {
        "success": True,
        "old_status": old_status,
        "new_status": new_status,
        "project": _project_to_dict(project),
        "advanced_by": current_user.full_name or current_user.username,
    }


def _project_to_dict(p: Project) -> dict:
    return {
        "id": str(p.id),
        "code": p.code,
        "name": p.name,
        "description": p.description,
        "infrastructure_class_id": str(p.infrastructure_class_id),
        "infrastructure_class_code": p.infrastructure_class_code,
        "asset_type_id": str(p.asset_type_id),
        "asset_type_name": p.asset_type_name,
        "status": p.status,
        "location": p.location.model_dump() if p.location else {},
        "estimated_cost": p.estimated_cost,
        "sanctioned_cost": p.sanctioned_cost,
        "actual_cost": p.actual_cost,
        "start_date": p.start_date.isoformat() if p.start_date else None,
        "expected_completion": p.expected_completion.isoformat() if p.expected_completion else None,
        "actual_completion": p.actual_completion.isoformat() if p.actual_completion else None,
        "contractor": p.contractor,
        "supervising_officer": p.supervising_officer,
        "department": p.department,
        "asset_id": str(p.asset_id) if p.asset_id else None,
        "created_by": p.created_by,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }
