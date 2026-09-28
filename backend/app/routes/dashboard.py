"""
Dashboard Routes — Executive KPIs, Lifecycle Analytics, Risk Matrix & Geo-spatial asset summaries.
"""

from fastapi import APIRouter, Depends
from datetime import datetime, date
from typing import Dict, List, Any

from app.models.asset import Asset
from app.models.project import Project
from app.models.inspection import Inspection
from app.models.maintenance import MaintenanceRecord
from app.models.issue import Issue
from app.models.lifecycle import LifecycleEvent
from app.auth.utils import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Aggregate high-level platform statistics for R&B leadership."""
    # Assets counts
    total_assets = await Asset.find(Asset.is_active == True).count()
    total_projects = await Project.find().count()
    active_projects = await Project.find(
        Project.status != "CLOSED", Project.status != "HANDOVER"
    ).count()

    # Financials
    all_assets = await Asset.find(Asset.is_active == True).to_list()
    total_estimated_value = sum(a.estimated_value or 0.0 for a in all_assets)
    total_replacement_value = sum(a.replacement_value or 0.0 for a in all_assets)

    # Risk Breakdown
    risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0, "NOT_ASSESSED": 0}
    for a in all_assets:
        level = a.current_risk_level or "NOT_ASSESSED"
        risk_counts[level] = risk_counts.get(level, 0) + 1

    # Condition Breakdown
    condition_counts = {"EXCELLENT": 0, "GOOD": 0, "FAIR": 0, "POOR": 0, "CRITICAL": 0, "NOT_ASSESSED": 0}
    for a in all_assets:
        rating = a.current_condition_rating or "NOT_ASSESSED"
        condition_counts[rating] = condition_counts.get(rating, 0) + 1

    # Infrastructure Class Breakdown
    class_stats = {
        "BUILDING": {"count": 0, "value": 0.0, "high_risk": 0},
        "ROAD": {"count": 0, "value": 0.0, "high_risk": 0},
        "BRIDGE": {"count": 0, "value": 0.0, "high_risk": 0},
    }
    for a in all_assets:
        code = a.infrastructure_class_code
        if code in class_stats:
            class_stats[code]["count"] += 1
            class_stats[code]["value"] += a.estimated_value or 0.0
            if a.current_risk_level in ["HIGH", "CRITICAL"]:
                class_stats[code]["high_risk"] += 1

    # Lifecycle Stage Distribution
    lifecycle_distribution = {}
    for a in all_assets:
        stage = a.current_stage or "CREATED"
        lifecycle_distribution[stage] = lifecycle_distribution.get(stage, 0) + 1

    # Pending Operations
    pending_inspections = await Inspection.find(
        Inspection.requires_immediate_action == True
    ).count()
    open_maintenance = await MaintenanceRecord.find(
        {"status": {"$in": ["PLANNED", "SCHEDULED", "IN_PROGRESS"]}}
    ).count()
    open_issues = await Issue.find(Issue.status == "OPEN").count()

    # Critical Alerts
    critical_assets = [
        {
            "id": str(a.id),
            "code": a.code,
            "name": a.name,
            "infrastructure_class_code": a.infrastructure_class_code,
            "district": a.location.district if a.location else "",
            "condition_rating": a.current_condition_rating,
            "condition_score": a.current_condition_score,
            "risk_level": a.current_risk_level,
            "risk_score": a.risk_score,
            "next_action": a.next_action,
            "next_action_due": a.next_action_due.isoformat() if a.next_action_due else None,
            "next_action_priority": a.next_action_priority,
        }
        for a in all_assets
        if a.current_risk_level in ["CRITICAL", "HIGH"] or a.current_condition_rating in ["POOR", "CRITICAL"]
    ]

    # Recent Activity Feed
    latest_events = await LifecycleEvent.find().sort("-transition_date").limit(8).to_list()
    activity_feed = []
    for ev in latest_events:
        asset = await Asset.get(ev.asset_id)
        activity_feed.append({
            "id": str(ev.id),
            "asset_id": str(ev.asset_id),
            "asset_name": asset.name if asset else "Asset",
            "type": "lifecycle_transition",
            "from_stage": ev.from_stage,
            "to_stage": ev.to_stage,
            "performed_by": ev.performed_by,
            "date": ev.transition_date.isoformat(),
            "notes": ev.notes,
        })

    return {
        "kpis": {
            "total_assets": total_assets,
            "total_projects": total_projects,
            "active_projects": active_projects,
            "critical_risk_assets": risk_counts.get("CRITICAL", 0),
            "high_risk_assets": risk_counts.get("HIGH", 0),
            "pending_inspections": pending_inspections,
            "open_maintenance": open_maintenance,
            "open_issues": open_issues,
            "total_estimated_value_cr": round(total_estimated_value / 100, 2),  # in Crores (Lakhs / 100)
            "total_replacement_value_cr": round(total_replacement_value / 100, 2),
        },
        "class_breakdown": class_stats,
        "risk_breakdown": risk_counts,
        "condition_breakdown": condition_counts,
        "lifecycle_distribution": lifecycle_distribution,
        "critical_alerts": critical_assets[:10],
        "activity_feed": activity_feed,
    }


@router.get("/geo-assets")
async def get_geo_assets(current_user: User = Depends(get_current_user)):
    """Return map points of assets with GPS coords for GIS visualizer."""
    assets = await Asset.find(
        {"is_active": True, "location.latitude": {"$ne": None}, "location.longitude": {"$ne": None}}
    ).to_list()

    return [
        {
            "id": str(a.id),
            "code": a.code,
            "name": a.name,
            "class_code": a.infrastructure_class_code,
            "asset_type": a.asset_type_name,
            "district": a.location.district if a.location else "",
            "lat": a.location.latitude,
            "lng": a.location.longitude,
            "condition_rating": a.current_condition_rating,
            "condition_score": a.current_condition_score,
            "risk_level": a.current_risk_level,
            "current_stage": a.current_stage,
            "next_action": a.next_action,
        }
        for a in assets
    ]
