"""
Risk Engine — Simple but meaningful risk scoring.

Risk = f(Condition, Criticality, Safety Impact, Service Impact)
No AI, no magic — just clear rules that make the system look intelligent.
"""

from datetime import date, datetime
from typing import Optional
from beanie import PydanticObjectId

from app.models.asset import Asset
from app.models.risk import RiskAssessment


# ── Risk Level Mapping ───────────────────────────────────────────────────────

RISK_LEVELS = {
    "LOW": {"score_range": (0, 25), "color": "#22C55E"},
    "MEDIUM": {"score_range": (26, 50), "color": "#F59E0B"},
    "HIGH": {"score_range": (51, 75), "color": "#F97316"},
    "CRITICAL": {"score_range": (76, 100), "color": "#EF4444"},
}

IMPACT_SCORES = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def compute_condition_risk(condition_score: Optional[float]) -> tuple[str, float]:
    """Convert condition score to risk contribution."""
    if condition_score is None:
        return "MEDIUM", 50.0

    # Inverse relationship: lower condition = higher risk
    if condition_score >= 80:
        return "LOW", 20.0
    elif condition_score >= 60:
        return "MEDIUM", 40.0
    elif condition_score >= 40:
        return "HIGH", 65.0
    else:
        return "CRITICAL", 90.0


def compute_overall_risk(
    condition_score: Optional[float],
    criticality: str = "MEDIUM",
    safety_impact: str = "LOW",
    service_impact: str = "LOW",
    infrastructure_class: str = "BUILDING",
) -> dict:
    """
    Compute overall risk level from multiple factors.
    Returns risk assessment data dict.
    """
    # Factor weights (infrastructure-specific)
    weights = {
        "BRIDGE": {"condition": 0.35, "criticality": 0.20, "safety": 0.30, "service": 0.15},
        "ROAD": {"condition": 0.30, "criticality": 0.20, "safety": 0.25, "service": 0.25},
        "BUILDING": {"condition": 0.30, "criticality": 0.25, "safety": 0.25, "service": 0.20},
    }

    w = weights.get(infrastructure_class, weights["BUILDING"])

    # Compute factor scores (0-100)
    cond_level, cond_score = compute_condition_risk(condition_score)
    crit_score = IMPACT_SCORES.get(criticality, 2) * 25
    safety_score = IMPACT_SCORES.get(safety_impact, 1) * 25
    service_score = IMPACT_SCORES.get(service_impact, 1) * 25

    # Weighted risk score
    risk_score = (
        w["condition"] * cond_score
        + w["criticality"] * crit_score
        + w["safety"] * safety_score
        + w["service"] * service_score
    )

    # Determine risk level
    if risk_score >= 75:
        overall = "CRITICAL"
    elif risk_score >= 50:
        overall = "HIGH"
    elif risk_score >= 25:
        overall = "MEDIUM"
    else:
        overall = "LOW"

    # Bridge + Critical condition = always CRITICAL
    if infrastructure_class == "BRIDGE" and cond_level == "CRITICAL":
        overall = "CRITICAL"
        risk_score = max(risk_score, 85)

    # Determine probability and consequence
    if condition_score and condition_score < 40:
        probability = "HIGH"
    elif condition_score and condition_score < 60:
        probability = "MEDIUM"
    else:
        probability = "LOW"

    max_impact = max(
        IMPACT_SCORES.get(criticality, 2),
        IMPACT_SCORES.get(safety_impact, 1),
        IMPACT_SCORES.get(service_impact, 1),
    )
    consequence_map = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
    consequence = consequence_map.get(max_impact, "MEDIUM")

    return {
        "risk_score": round(risk_score, 1),
        "overall_risk": overall,
        "probability": probability,
        "consequence": consequence,
        "condition_risk": cond_level,
        "factors": {
            "condition": {"score": cond_score, "weight": w["condition"], "level": cond_level},
            "criticality": {"score": crit_score, "weight": w["criticality"], "level": criticality},
            "safety": {"score": safety_score, "weight": w["safety"], "level": safety_impact},
            "service": {"score": service_score, "weight": w["service"], "level": service_impact},
        },
    }


def get_risk_recommendation(
    overall_risk: str,
    infrastructure_class: str,
    condition_rating: str = "NOT_ASSESSED",
) -> dict:
    """Get risk-based recommendations."""
    recommendations = {
        ("CRITICAL", "BRIDGE"): {
            "action": "Urgent structural inspection and safety assessment required",
            "mitigations": [
                "Restrict traffic load immediately",
                "Deploy emergency inspection team",
                "Prepare closure plan if needed",
            ],
        },
        ("CRITICAL", "ROAD"): {
            "action": "Emergency road safety assessment and closure evaluation",
            "mitigations": [
                "Assess structural integrity",
                "Implement speed restrictions",
                "Plan emergency rehabilitation",
            ],
        },
        ("CRITICAL", "BUILDING"): {
            "action": "Immediate structural safety assessment",
            "mitigations": [
                "Evacuate if necessary",
                "Engage structural engineer",
                "Plan emergency strengthening",
            ],
        },
        ("HIGH", "BRIDGE"): {
            "action": "Schedule detailed structural inspection within 30 days",
            "mitigations": [
                "Monitor for further deterioration",
                "Plan rehabilitation assessment",
                "Review load restrictions",
            ],
        },
        ("HIGH", "ROAD"): {
            "action": "Schedule rehabilitation assessment within 60 days",
            "mitigations": [
                "Implement temporary repairs",
                "Plan resurfacing or overlay",
                "Monitor traffic safety",
            ],
        },
        ("HIGH", "BUILDING"): {
            "action": "Schedule major maintenance assessment within 60 days",
            "mitigations": [
                "Identify critical repairs",
                "Plan corrective maintenance",
                "Review safety systems",
            ],
        },
    }

    key = (overall_risk, infrastructure_class)
    if key in recommendations:
        return recommendations[key]

    if overall_risk == "MEDIUM":
        return {
            "action": "Schedule preventive maintenance",
            "mitigations": ["Continue routine monitoring", "Plan preservation work"],
        }

    return {
        "action": "Continue routine monitoring and scheduled inspections",
        "mitigations": ["Maintain inspection schedule", "Document condition changes"],
    }


async def assess_risk_for_asset(
    asset: Asset,
    criticality: str = "MEDIUM",
    safety_impact: str = "LOW",
    service_impact: str = "LOW",
) -> RiskAssessment:
    """Create a new risk assessment for an asset and update the asset."""
    risk_data = compute_overall_risk(
        condition_score=asset.current_condition_score,
        criticality=criticality,
        safety_impact=safety_impact,
        service_impact=service_impact,
        infrastructure_class=asset.infrastructure_class_code,
    )

    rec = get_risk_recommendation(
        risk_data["overall_risk"],
        asset.infrastructure_class_code,
        asset.current_condition_rating,
    )

    assessment = RiskAssessment(
        asset_id=asset.id,
        assessment_date=date.today(),
        condition_score=asset.current_condition_score or 50,
        condition_rating=asset.current_condition_rating,
        criticality=criticality,
        safety_impact=safety_impact,
        service_impact=service_impact,
        probability=risk_data["probability"],
        consequence=risk_data["consequence"],
        overall_risk=risk_data["overall_risk"],
        risk_score=risk_data["risk_score"],
        factors=risk_data["factors"],
        recommendations=rec["action"],
        mitigation_actions=rec["mitigations"],
    )
    await assessment.insert()

    # Update asset risk fields
    asset.current_risk_level = risk_data["overall_risk"]
    asset.risk_score = risk_data["risk_score"]
    asset.updated_at = datetime.utcnow()
    await asset.save()

    return assessment


def calculate_risk_level(condition_score: Optional[float]) -> str:
    """Simple helper — condition score to risk level."""
    if condition_score is None:
        return "NOT_ASSESSED"
    if condition_score >= 80:
        return "LOW"
    elif condition_score >= 60:
        return "MEDIUM"
    elif condition_score >= 40:
        return "HIGH"
    else:
        return "CRITICAL"
