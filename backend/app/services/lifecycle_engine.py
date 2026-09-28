"""
Lifecycle Engine — The core state machine that drives the entire platform.

This is NOT frontend logic. It validates transitions, enforces rules,
creates audit events, and calculates next actions.
"""

from datetime import datetime, date
from typing import Optional
from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.models.asset import Asset
from app.models.lifecycle import LifecycleTemplate, LifecycleEvent


async def get_template_for_asset(asset: Asset) -> Optional[LifecycleTemplate]:
    """Find the lifecycle template for an asset's infrastructure class."""
    if asset.lifecycle_template_id:
        return await LifecycleTemplate.get(asset.lifecycle_template_id)
    # Fallback: find by infrastructure class code
    return await LifecycleTemplate.find_one(
        LifecycleTemplate.infrastructure_class_code == asset.infrastructure_class_code,
        LifecycleTemplate.is_active == True,
    )


async def get_allowed_transitions(asset: Asset) -> list[dict]:
    """Get the list of allowed transitions from the current stage."""
    template = await get_template_for_asset(asset)
    if not template:
        return []

    allowed = []
    for transition in template.transitions:
        if transition.from_stage == asset.current_stage:
            # Find the target stage details
            target_stage = next(
                (s for s in template.stages if s.code == transition.to_stage), None
            )
            allowed.append({
                "to_stage": transition.to_stage,
                "stage_name": target_stage.name if target_stage else transition.to_stage,
                "requires_condition_assessment": transition.requires_condition_assessment,
                "requires_inspection": transition.requires_inspection,
                "required_fields": transition.required_fields,
                "description": transition.description,
            })
    return allowed


async def get_current_stage_info(asset: Asset) -> Optional[dict]:
    """Get detailed info about the current lifecycle stage."""
    template = await get_template_for_asset(asset)
    if not template:
        return None

    stage = next(
        (s for s in template.stages if s.code == asset.current_stage), None
    )
    if not stage:
        return None

    return {
        "code": stage.code,
        "name": stage.name,
        "description": stage.description,
        "order": stage.order,
        "stage_type": stage.stage_type,
        "is_terminal": stage.is_terminal,
    }


async def validate_transition(
    asset: Asset, to_stage: str, notes: str = ""
) -> dict:
    """
    Validate if a transition is allowed.
    Returns validation result with details.
    """
    template = await get_template_for_asset(asset)
    if not template:
        return {
            "valid": False,
            "error": "No lifecycle template found for this asset",
        }

    # Find the transition rule
    transition_rule = next(
        (
            t
            for t in template.transitions
            if t.from_stage == asset.current_stage and t.to_stage == to_stage
        ),
        None,
    )

    if not transition_rule:
        allowed = [
            t.to_stage
            for t in template.transitions
            if t.from_stage == asset.current_stage
        ]
        return {
            "valid": False,
            "error": f"Transition from '{asset.current_stage}' to '{to_stage}' is not allowed. Allowed transitions: {allowed}",
        }

    # Check if condition assessment is required
    if transition_rule.requires_condition_assessment:
        if not asset.current_condition_score and asset.current_condition_rating == "NOT_ASSESSED":
            return {
                "valid": False,
                "error": f"Transition to '{to_stage}' requires a condition assessment first",
            }

    return {
        "valid": True,
        "transition_rule": {
            "from_stage": transition_rule.from_stage,
            "to_stage": transition_rule.to_stage,
            "description": transition_rule.description,
        },
    }


async def execute_transition(
    asset: Asset,
    to_stage: str,
    performed_by: str = "System",
    notes: str = "",
    metadata: dict = None,
) -> Asset:
    """
    Execute a lifecycle transition:
    1. Validate current stage
    2. Validate allowed transition
    3. Update asset stage
    4. Create lifecycle event
    5. Calculate next action
    6. Return updated asset
    """
    # Step 1 & 2: Validate
    validation = await validate_transition(asset, to_stage, notes)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["error"],
        )

    # Step 3: Update asset
    previous_stage = asset.current_stage
    asset.previous_stage = previous_stage
    asset.current_stage = to_stage
    asset.updated_at = datetime.utcnow()

    # Step 4: Create lifecycle event
    event = LifecycleEvent(
        asset_id=asset.id,
        from_stage=previous_stage,
        to_stage=to_stage,
        transition_date=datetime.utcnow(),
        performed_by=performed_by,
        notes=notes,
        metadata=metadata or {},
    )
    await event.insert()

    # Step 5: Calculate next action based on new stage
    await calculate_next_action(asset)

    # Step 6: Save and return
    await asset.save()

    return asset


async def calculate_next_action(asset: Asset) -> None:
    """
    Determine the recommended next action based on the asset's current state.
    Updates the asset's next_action fields in place.
    """
    from app.services.risk_engine import calculate_risk_level
    from app.models.inspection import Inspection

    stage = asset.current_stage
    infra = asset.infrastructure_class_code
    condition = asset.current_condition_rating
    score = asset.current_condition_score

    # ── Stage-based next actions ─────────────────────────────────────────────
    stage_actions = {
        "CREATED": ("Assign lifecycle template and begin planning", "NORMAL"),
        "PLANNING": ("Complete planning and proceed to design/survey", "NORMAL"),
        "DESIGN": ("Complete design and proceed to approvals", "NORMAL"),
        "APPROVAL": ("Obtain approvals and proceed to tendering", "NORMAL"),
        "TENDER": ("Complete tendering and award contract", "NORMAL"),
        "CONSTRUCTION": ("Monitor construction progress", "NORMAL"),
        "QUALITY_ACCEPTANCE": ("Complete quality acceptance checks", "HIGH"),
        "COMMISSIONING": ("Commission the asset and prepare for handover", "HIGH"),
        "HANDOVER": ("Complete handover and prepare asset passport", "HIGH"),
    }

    if stage in stage_actions:
        asset.next_action, asset.next_action_priority = stage_actions[stage]
        return

    # ── Operational stage — condition-driven next actions ─────────────────────
    if stage in ("OPERATIONAL", "OPEN_TO_TRAFFIC"):
        # Check if inspection is overdue
        if asset.next_inspection_due and asset.next_inspection_due < date.today():
            asset.next_action = "Inspection overdue — schedule immediately"
            asset.next_action_priority = "URGENT"
            asset.next_action_due = date.today()
            return

        # Check if inspection is coming up
        if asset.next_inspection_due:
            days_until = (asset.next_inspection_due - date.today()).days
            if days_until <= 30:
                asset.next_action = f"Inspection due in {days_until} days"
                asset.next_action_priority = "HIGH"
                asset.next_action_due = asset.next_inspection_due
                return

        # Condition-based recommendations
        if condition == "CRITICAL":
            asset.next_action = "URGENT: Immediate safety assessment and intervention required"
            asset.next_action_priority = "URGENT"
            asset.next_action_due = date.today()
        elif condition == "POOR":
            if infra == "ROAD":
                asset.next_action = "Rehabilitation assessment recommended"
            elif infra == "BRIDGE":
                asset.next_action = "Structural inspection and rehabilitation assessment"
            else:
                asset.next_action = "Major maintenance or rehabilitation assessment"
            asset.next_action_priority = "HIGH"
        elif condition == "FAIR":
            if infra == "ROAD":
                asset.next_action = "Schedule preventive preservation"
            elif infra == "BRIDGE":
                asset.next_action = "Preventive maintenance recommended"
            else:
                asset.next_action = "Schedule preventive maintenance"
            asset.next_action_priority = "NORMAL"
        elif condition == "GOOD":
            asset.next_action = "Continue routine monitoring"
            asset.next_action_priority = "LOW"
        else:
            asset.next_action = "Schedule initial condition assessment"
            asset.next_action_priority = "NORMAL"
        return

    # ── Maintenance/Inspection stages ────────────────────────────────────────
    maintenance_actions = {
        "INSPECTION": ("Complete inspection and record findings", "HIGH"),
        "ROUTINE_INSPECTION": ("Complete routine inspection", "NORMAL"),
        "CONDITION_ASSESSMENT": ("Complete condition assessment and determine intervention", "HIGH"),
        "MAINTENANCE": ("Complete maintenance work and update condition", "NORMAL"),
        "ROUTINE_MAINTENANCE": ("Complete routine maintenance", "NORMAL"),
        "PREVENTIVE_PRESERVATION": ("Complete preventive preservation work", "NORMAL"),
        "REPAIR": ("Complete repair work and verify", "HIGH"),
        "RENOVATION": ("Complete renovation and update asset passport", "NORMAL"),
        "REHABILITATION": ("Complete rehabilitation and reassess condition", "HIGH"),
        "STRENGTHENING": ("Complete strengthening work and re-inspect", "HIGH"),
        "RECONSTRUCTION": ("Complete reconstruction", "HIGH"),
        "PERIODIC_RENEWAL": ("Complete periodic renewal", "NORMAL"),
    }

    if stage in maintenance_actions:
        asset.next_action, asset.next_action_priority = maintenance_actions[stage]
        return

    # ── Terminal stages ──────────────────────────────────────────────────────
    terminal_actions = {
        "RETIREMENT": ("Prepare for demolition or disposal", "LOW"),
        "CLOSURE": ("Prepare closure documentation", "LOW"),
        "DEMOLITION": ("Complete demolition and update records", "NORMAL"),
        "DISPOSAL": ("Complete disposal process", "NORMAL"),
        "DECOMMISSIONING": ("Complete decommissioning", "NORMAL"),
    }

    if stage in terminal_actions:
        asset.next_action, asset.next_action_priority = terminal_actions[stage]
        return

    # Fallback
    asset.next_action = "Review current status"
    asset.next_action_priority = "NORMAL"


async def get_lifecycle_timeline(asset_id: PydanticObjectId) -> list[dict]:
    """Get the complete lifecycle event history for an asset."""
    events = await LifecycleEvent.find(
        LifecycleEvent.asset_id == asset_id
    ).sort("+transition_date").to_list()

    return [
        {
            "id": str(e.id),
            "from_stage": e.from_stage,
            "to_stage": e.to_stage,
            "transition_date": e.transition_date.isoformat(),
            "performed_by": e.performed_by,
            "notes": e.notes,
            "metadata": e.metadata,
        }
        for e in events
    ]
