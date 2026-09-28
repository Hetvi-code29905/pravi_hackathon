"""
Database Seeder for Gujarat Roads & Buildings (R&B) Infrastructure Platform.
Populates standard infrastructure classes, asset types, lifecycle templates,
default users, realistic projects, and physical assets with GPS coords, condition histories,
inspections, components, and maintenance records.
"""

from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends
from app.auth.utils import hash_password
from app.auth.models import User
from app.models.infrastructure import InfrastructureClass
from app.models.asset_type import AssetType
from app.models.lifecycle import LifecycleTemplate, LifecycleStageDefinition, LifecycleTransitionRule, ConditionThreshold, LifecycleEvent
from app.models.project import Project, ProjectLocation
from app.models.asset import Asset, AssetLocation, AssetResponsibility, PlannedLifecycle
from app.models.condition import ConditionAssessment
from app.models.inspection import Inspection
from app.models.maintenance import MaintenanceRecord
from app.models.issue import Issue
from app.models.component import AssetComponent
from app.models.document import AssetDocument
from app.models.cost import AssetCost
from app.models.risk import RiskAssessment
from app.services.risk_engine import assess_risk_for_asset, compute_overall_risk

seed_router = APIRouter(prefix="/api", tags=["Seed"])


async def run_seed():
    print("[SEED] Starting R&B Lifecycle Platform Database Seeding...")

    # 1. Clear existing collections for a clean idempotent seed
    await User.find().delete()
    await InfrastructureClass.find().delete()
    await AssetType.find().delete()
    await LifecycleTemplate.find().delete()
    await LifecycleEvent.find().delete()
    await Project.find().delete()
    await Asset.find().delete()
    await ConditionAssessment.find().delete()
    await Inspection.find().delete()
    await MaintenanceRecord.find().delete()
    await Issue.find().delete()
    await AssetComponent.find().delete()
    await AssetDocument.find().delete()
    await AssetCost.find().delete()
    await RiskAssessment.find().delete()

    # 2. Seed Users - All 5 Key Government & Industry Stakeholders
    secretary_user = User(
        username="secretary@rnb.gujarat.gov.in",
        email="secretary@rnb.gujarat.gov.in",
        password_hash=hash_password("secretary123"),
        full_name="Shri M. K. Das, IAS",
        role="SECRETARY",
        department="Roads & Buildings Department, Govt. of Gujarat",
        designation="Principal Secretary (R&B)",
    )
    await secretary_user.insert()

    admin_user = User(
        username="admin@rnb.gujarat.gov.in",
        email="admin@rnb.gujarat.gov.in",
        password_hash=hash_password("admin123"),
        full_name="Shri Rajesh Patel (Chief Engineer)",
        role="ADMIN",
        department="Gujarat Roads & Buildings Department",
        designation="Chief Engineer & State Asset Director",
    )
    await admin_user.insert()

    engineer_user = User(
        username="engineer@rnb.gujarat.gov.in",
        email="engineer@rnb.gujarat.gov.in",
        password_hash=hash_password("engineer123"),
        full_name="Er. Amit Shah",
        role="ENGINEER",
        department="Capital Project Division, Gandhinagar",
        designation="Executive Engineer",
    )
    await engineer_user.insert()

    inspector_user = User(
        username="inspector@rnb.gujarat.gov.in",
        email="inspector@rnb.gujarat.gov.in",
        password_hash=hash_password("inspector123"),
        full_name="Smt. Priya Desai",
        role="INSPECTOR",
        department="Quality Control & Inspection Wing",
        designation="Assistant Executive Engineer (QC)",
    )
    await inspector_user.insert()

    contractor_user = User(
        username="contractor@rnb.gujarat.gov.in",
        email="contractor@rnb.gujarat.gov.in",
        password_hash=hash_password("contractor123"),
        full_name="M/s L&T Infrastructure Engineering",
        role="CONTRACTOR",
        department="EPC Concessionaire Partner",
        designation="Authorized Signatory / Project Lead",
    )
    await contractor_user.insert()

    # 3. Seed Infrastructure Classes
    bld_class = InfrastructureClass(
        code="BUILDING",
        name="Government Buildings & Complexes",
        description="Public administrative complexes, government hospitals, educational colleges, collectorates, and courts.",
        icon="Building",
        color="#3B82F6",
        is_active=True,
    )
    await bld_class.insert()

    road_class = InfrastructureClass(
        code="ROAD",
        name="Roads & Highway Networks",
        description="State Highways (SH), Major District Roads (MDR), arterials, bypass expressways, and urban connectors.",
        icon="Road",
        color="#10B981",
        is_active=True,
    )
    await road_class.insert()

    brg_class = InfrastructureClass(
        code="BRIDGE",
        name="Bridges, Flyovers & Grade Separators",
        description="Major river bridges, railway over bridges (ROB), cable-stayed structures, and grade-separated flyovers.",
        icon="Waypoints",
        color="#F59E0B",
        is_active=True,
    )
    await brg_class.insert()

    # 4. Seed Asset Types
    hospital_type = AssetType(
        code="HOSPITAL",
        name="District Civil Hospital & Medical College",
        infrastructure_class_id=bld_class.id,
        infrastructure_class_code=bld_class.code,
        description="Multi-story healthcare facility with 24x7 critical public operation.",
        default_inspection_interval_days=180,
    )
    await hospital_type.insert()

    collectorate_type = AssetType(
        code="COLLECTORATE",
        name="District Collectorate & Administrative Complex",
        infrastructure_class_id=bld_class.id,
        infrastructure_class_code=bld_class.code,
        description="Headquarters for revenue and district administration.",
        default_inspection_interval_days=365,
    )
    await collectorate_type.insert()

    college_type = AssetType(
        code="GOVT_COLLEGE",
        name="Government Engineering College / Polytechnic",
        infrastructure_class_id=bld_class.id,
        infrastructure_class_code=bld_class.code,
        description="Institutional higher-education infrastructure.",
        default_inspection_interval_days=365,
    )
    await college_type.insert()

    sh_type = AssetType(
        code="STATE_HIGHWAY",
        name="State Highway (SH)",
        infrastructure_class_id=road_class.id,
        infrastructure_class_code=road_class.code,
        description="High-capacity arterial roadway connecting district headquarters and industrial nodes.",
        default_inspection_interval_days=90,
    )
    await sh_type.insert()

    mdr_type = AssetType(
        code="MDR",
        name="Major District Road (MDR)",
        infrastructure_class_id=road_class.id,
        infrastructure_class_code=road_class.code,
        description="Secondary road connecting rural production centers with state highways.",
        default_inspection_interval_days=180,
    )
    await mdr_type.insert()

    river_brg_type = AssetType(
        code="RIVER_BRIDGE",
        name="Major River Bridge / Cable-Stayed",
        infrastructure_class_id=brg_class.id,
        infrastructure_class_code=brg_class.code,
        description="Critical bridge crossing rivers or major water bodies requiring rigorous structural monitoring.",
        default_inspection_interval_days=90,
    )
    await river_brg_type.insert()

    flyover_type = AssetType(
        code="FLYOVER",
        name="Elevated Corridor / Urban Flyover",
        infrastructure_class_id=brg_class.id,
        infrastructure_class_code=brg_class.code,
        description="Prestressed concrete grade separator reducing urban vehicular congestion.",
        default_inspection_interval_days=180,
    )
    await flyover_type.insert()

    # 5. Seed Lifecycle Templates
    # Building Lifecycle Template
    bld_stages = [
        LifecycleStageDefinition(code="PLANNING", name="Planning & Feasibility", order=1, description="Need sanction & land verification"),
        LifecycleStageDefinition(code="CONSTRUCTION", name="Construction Phase", order=2, description="Active civil execution"),
        LifecycleStageDefinition(code="COMMISSIONED", name="Commissioned & Handed Over", order=3, description="Formal handover to user dept"),
        LifecycleStageDefinition(code="OPERATIONAL", name="Operational & In Use", order=4, description="Standard operational lifecycle"),
        LifecycleStageDefinition(code="MAINTENANCE", name="Routine & Preventive Maintenance", order=5, description="Planned repair cycles"),
        LifecycleStageDefinition(code="REHABILITATION", name="Major Structural Rehabilitation", order=6, description="Retrofitting & life extension"),
        LifecycleStageDefinition(code="DECOMMISSIONED", name="Decommissioned", order=7, is_terminal=True, description="Asset retired from service"),
    ]
    bld_transitions = [
        LifecycleTransitionRule(from_stage="PLANNING", to_stage="CONSTRUCTION", description="Work order awarded and construction begins"),
        LifecycleTransitionRule(from_stage="CONSTRUCTION", to_stage="COMMISSIONED", requires_inspection=True, description="Completion certificate & inspection passed"),
        LifecycleTransitionRule(from_stage="COMMISSIONED", to_stage="OPERATIONAL", description="Handover completed and occupancy authorized"),
        LifecycleTransitionRule(from_stage="OPERATIONAL", to_stage="MAINTENANCE", description="Periodic or condition-based maintenance scheduled"),
        LifecycleTransitionRule(from_stage="MAINTENANCE", to_stage="OPERATIONAL", requires_inspection=True, description="Maintenance completed and verified"),
        LifecycleTransitionRule(from_stage="OPERATIONAL", to_stage="REHABILITATION", requires_condition_assessment=True, description="Condition degraded below acceptable threshold"),
        LifecycleTransitionRule(from_stage="REHABILITATION", to_stage="OPERATIONAL", requires_inspection=True, description="Rehabilitation completed successfully"),
        LifecycleTransitionRule(from_stage="REHABILITATION", to_stage="DECOMMISSIONED", description="Structure declared unsafe for further rehabilitation"),
    ]
    bld_thresholds = [
        ConditionThreshold(rating="EXCELLENT", min_score=85, max_score=100, recommended_action="Routine Inspection", color="#22C55E"),
        ConditionThreshold(rating="GOOD", min_score=70, max_score=84, recommended_action="Preventive Maintenance", color="#3B82F6"),
        ConditionThreshold(rating="FAIR", min_score=50, max_score=69, recommended_action="Targeted Repairs", color="#F59E0B"),
        ConditionThreshold(rating="POOR", min_score=35, max_score=49, recommended_action="Major Structural Rehabilitation", color="#F97316"),
        ConditionThreshold(rating="CRITICAL", min_score=0, max_score=34, recommended_action="Immediate Safety Audit & Closure Evaluation", color="#EF4444"),
    ]
    bld_template = LifecycleTemplate(
        code="LT-BUILDING-STD",
        name="Gujarat R&B Standard Building Lifecycle",
        infrastructure_class_code="BUILDING",
        description="Standard CPWD/R&B lifecycle state machine for public administrative and healthcare facilities.",
        stages=bld_stages,
        transitions=bld_transitions,
        condition_thresholds=bld_thresholds,
    )
    await bld_template.insert()

    # Road Lifecycle Template
    road_stages = [
        LifecycleStageDefinition(code="PLANNING", name="DPR & Tender", order=1),
        LifecycleStageDefinition(code="CONSTRUCTION", name="Pavement Construction", order=2),
        LifecycleStageDefinition(code="COMMISSIONED", name="Commissioned & Open to Traffic", order=3),
        LifecycleStageDefinition(code="DEFECT_LIABILITY", name="Defect Liability Period (DLP)", order=4, description="Contractor maintenance guarantee"),
        LifecycleStageDefinition(code="OPERATIONAL", name="Operational Maintenance", order=5),
        LifecycleStageDefinition(code="PERIODIC_RENEWAL", name="Bituminous Renewal / Resurfacing", order=6),
        LifecycleStageDefinition(code="REHABILITATION", name="Major Reconstruction & Widening", order=7),
    ]
    road_transitions = [
        LifecycleTransitionRule(from_stage="PLANNING", to_stage="CONSTRUCTION", description="Tender finalized"),
        LifecycleTransitionRule(from_stage="CONSTRUCTION", to_stage="COMMISSIONED", requires_inspection=True),
        LifecycleTransitionRule(from_stage="COMMISSIONED", to_stage="DEFECT_LIABILITY"),
        LifecycleTransitionRule(from_stage="DEFECT_LIABILITY", to_stage="OPERATIONAL", requires_inspection=True, description="DLP clearance"),
        LifecycleTransitionRule(from_stage="OPERATIONAL", to_stage="PERIODIC_RENEWAL"),
        LifecycleTransitionRule(from_stage="PERIODIC_RENEWAL", to_stage="OPERATIONAL", requires_inspection=True),
        LifecycleTransitionRule(from_stage="OPERATIONAL", to_stage="REHABILITATION", requires_condition_assessment=True),
        LifecycleTransitionRule(from_stage="REHABILITATION", to_stage="OPERATIONAL", requires_inspection=True),
    ]
    road_template = LifecycleTemplate(
        code="LT-ROAD-STD",
        name="Gujarat R&B Highway Lifecycle Model",
        infrastructure_class_code="ROAD",
        description="IRC/PIARC aligned road pavement lifecycle managing renewal cycles and PCI (Pavement Condition Index).",
        stages=road_stages,
        transitions=road_transitions,
        condition_thresholds=bld_thresholds,
    )
    await road_template.insert()

    # Bridge Lifecycle Template
    brg_stages = [
        LifecycleStageDefinition(code="DESIGN", name="Design & Hydraulic Clearance", order=1),
        LifecycleStageDefinition(code="CONSTRUCTION", name="Superstructure & Substructure Execution", order=2),
        LifecycleStageDefinition(code="COMMISSIONED", name="Load Tested & Commissioned", order=3),
        LifecycleStageDefinition(code="OPERATIONAL", name="Active Service", order=4),
        LifecycleStageDefinition(code="SPECIAL_MONITORING", name="Special Structural Monitoring", order=5, description="High risk or aging bearings/cables"),
        LifecycleStageDefinition(code="MAJOR_REHABILITATION", name="Major Structural Rehabilitation", order=6),
        LifecycleStageDefinition(code="DECOMMISSIONED", name="Decommissioned & Replaced", order=7, is_terminal=True),
    ]
    brg_transitions = [
        LifecycleTransitionRule(from_stage="DESIGN", to_stage="CONSTRUCTION"),
        LifecycleTransitionRule(from_stage="CONSTRUCTION", to_stage="COMMISSIONED", requires_inspection=True),
        LifecycleTransitionRule(from_stage="COMMISSIONED", to_stage="OPERATIONAL"),
        LifecycleTransitionRule(from_stage="OPERATIONAL", to_stage="SPECIAL_MONITORING", requires_condition_assessment=True),
        LifecycleTransitionRule(from_stage="SPECIAL_MONITORING", to_stage="OPERATIONAL", requires_inspection=True),
        LifecycleTransitionRule(from_stage="SPECIAL_MONITORING", to_stage="MAJOR_REHABILITATION"),
        LifecycleTransitionRule(from_stage="MAJOR_REHABILITATION", to_stage="OPERATIONAL", requires_inspection=True),
        LifecycleTransitionRule(from_stage="MAJOR_REHABILITATION", to_stage="DECOMMISSIONED"),
    ]
    brg_template = LifecycleTemplate(
        code="LT-BRIDGE-STD",
        name="Gujarat R&B Bridge Management Lifecycle",
        infrastructure_class_code="BRIDGE",
        description="IRC:SP:35 compliant structural bridge management system emphasizing bearings, expansion joints, and piers.",
        stages=brg_stages,
        transitions=brg_transitions,
        condition_thresholds=bld_thresholds,
    )
    await brg_template.insert()

    # 6. Seed Realistic Projects
    projects_data = [
        {
            "code": "PRJ-2025-001",
            "name": "Ahmedabad-Gandhinagar SG Highway 6-Lane Elevated Corridor Ext.",
            "description": "Construction of 11.8 km elevated corridor to bypass congested junctions along SH-41.",
            "infrastructure_class_id": road_class.id,
            "infrastructure_class_code": "ROAD",
            "asset_type_id": sh_type.id,
            "status": "CONSTRUCTION",
            "location": ProjectLocation(state="Gujarat", district="Ahmedabad", taluka="Ghatlodia", city="Ahmedabad", latitude=23.0525, longitude=72.5312),
            "estimated_cost": 48500.0,
            "sanctioned_cost": 46200.0,
            "start_date": date(2024, 10, 1),
            "expected_completion": date(2026, 12, 31),
            "contractor": "Larsen & Toubro Infrastructure Ltd.",
            "supervising_officer": "Er. Amit Shah, EE R&B",
        },
        {
            "code": "PRJ-2025-002",
            "name": "Surat New Civil Hospital Super-Specialty 600-Bed Trauma Complex",
            "description": "Constructing state-of-the-art earthquake-resistant trauma building with 14 modular OTs.",
            "infrastructure_class_id": bld_class.id,
            "infrastructure_class_code": "BUILDING",
            "asset_type_id": hospital_type.id,
            "status": "HANDOVER",
            "location": ProjectLocation(state="Gujarat", district="Surat", taluka="Majura", city="Surat", latitude=21.1702, longitude=72.8311),
            "estimated_cost": 28500.0,
            "sanctioned_cost": 27900.0,
            "actual_cost": 27450.0,
            "start_date": date(2023, 4, 15),
            "expected_completion": date(2025, 11, 30),
            "contractor": "PSP Projects Ltd.",
            "supervising_officer": "Shri D.K. Rathod, SE R&B Surat",
        },
        {
            "code": "PRJ-2025-003",
            "name": "Narmada River Cable-Stayed Bridge Connecting Bharuch & Ankleshwar",
            "description": "Construction of landmark 1.4 km 4-lane cable-stayed river bridge to replace aging truss spans.",
            "infrastructure_class_id": brg_class.id,
            "infrastructure_class_code": "BRIDGE",
            "asset_type_id": river_brg_type.id,
            "status": "COMMISSIONING",
            "location": ProjectLocation(state="Gujarat", district="Bharuch", taluka="Bharuch", city="Bharuch", latitude=21.7051, longitude=72.9959),
            "estimated_cost": 37900.0,
            "sanctioned_cost": 37200.0,
            "start_date": date(2022, 1, 10),
            "expected_completion": date(2026, 3, 31),
            "contractor": "Afcons Infrastructure",
            "supervising_officer": "Er. K.N. Trivedi, EE Bharuch",
        },
        {
            "code": "PRJ-2025-004",
            "name": "Vadodara-Padra State Highway 11 Widening & Geometric Improvement",
            "description": "Pavement strengthening, drainage improvement, and junction remodeling for 22 km stretch.",
            "infrastructure_class_id": road_class.id,
            "infrastructure_class_code": "ROAD",
            "asset_type_id": sh_type.id,
            "status": "PLANNING",
            "location": ProjectLocation(state="Gujarat", district="Vadodara", taluka="Padra", city="Vadodara", latitude=22.2530, longitude=73.0850),
            "estimated_cost": 14200.0,
            "sanctioned_cost": 13800.0,
            "start_date": date(2026, 8, 1),
            "expected_completion": date(2028, 2, 28),
            "contractor": "Tendering Phase",
            "supervising_officer": "Er. S.R. Varma, EE Vadodara",
        },
    ]

    project_objs = []
    for pdata in projects_data:
        p = Project(**pdata)
        await p.insert()
        project_objs.append(p)

    # 7. Seed Physical Assets (The Heart of the Asset Passport)
    assets_data = [
        {
            "code": "R&B-BRG-00001",
            "name": "Atal Pedestrian Bridge, Sabarmati Riverfront",
            "description": "Iconic 300m pedestrian cable truss bridge spanning Sabarmati river between Ellis Bridge and Sardar Bridge.",
            "infrastructure_class_id": brg_class.id,
            "infrastructure_class_code": "BRIDGE",
            "asset_type_id": river_brg_type.id,
            "asset_type_name": river_brg_type.name,
            "lifecycle_template_id": brg_template.id,
            "current_stage": "OPERATIONAL",
            "location": AssetLocation(state="Gujarat", district="Ahmedabad", taluka="Ahmedabad City", city="Ahmedabad", address="Sabarmati Riverfront West, Ellisbridge", latitude=23.0225, longitude=72.5714),
            "commissioned_date": date(2022, 8, 27),
            "responsibility": AssetResponsibility(custodian="Roads & Buildings Department / AMC", operator="Sabarmati Riverfront Development Corp", maintenance_agency="R&B Special Bridge Division Ahmedabad"),
            "current_condition_score": 92.0,
            "current_condition_rating": "EXCELLENT",
            "current_risk_level": "LOW",
            "risk_score": 18.5,
            "next_action": "Routine Annual Structural Inspection",
            "next_action_due": date(2026, 11, 15),
            "next_action_priority": "LOW",
            "last_inspection_date": date(2025, 11, 10),
            "next_inspection_due": date(2026, 11, 10),
            "estimated_value": 7400.0,
            "replacement_value": 9800.0,
            "planned_lifecycle": PlannedLifecycle(design_life_years=75, expected_end_of_life=date(2097, 8, 27), initial_cost=7400.0),
        },
        {
            "code": "R&B-RD-00002",
            "name": "Sarkhej-Gandhinagar (SG) Highway Section KM 14-26",
            "description": "Key 12km high-density commercial corridor connecting Vaishnodevi Circle to Gandhinagar Koba.",
            "infrastructure_class_id": road_class.id,
            "infrastructure_class_code": "ROAD",
            "asset_type_id": sh_type.id,
            "asset_type_name": sh_type.name,
            "lifecycle_template_id": road_template.id,
            "current_stage": "OPERATIONAL",
            "location": AssetLocation(state="Gujarat", district="Gandhinagar", taluka="Gandhinagar", city="Gandhinagar", address="SH-41, SG Highway", latitude=23.1750, longitude=72.6050),
            "commissioned_date": date(2019, 3, 15),
            "responsibility": AssetResponsibility(custodian="R&B State Highway Division", operator="R&B Dept", maintenance_agency="Ahmedabad-Gandhinagar Maintenance Division"),
            "current_condition_score": 68.5,
            "current_condition_rating": "FAIR",
            "current_risk_level": "MEDIUM",
            "risk_score": 42.0,
            "next_action": "Bituminous Micro-surfacing & Wearing Course Replacement",
            "next_action_due": date(2026, 10, 20),
            "next_action_priority": "MEDIUM",
            "last_inspection_date": date(2026, 1, 14),
            "next_inspection_due": date(2026, 7, 14),
            "estimated_value": 24000.0,
            "replacement_value": 31000.0,
            "planned_lifecycle": PlannedLifecycle(design_life_years=25, expected_end_of_life=date(2044, 3, 15), initial_cost=21000.0),
        },
        {
            "code": "R&B-BLD-00003",
            "name": "Ahmedabad Civil Hospital New Trauma & OPD Complex",
            "description": "1200-bed apex trauma centre and outpatient multi-story complex serving central Gujarat.",
            "infrastructure_class_id": bld_class.id,
            "infrastructure_class_code": "BUILDING",
            "asset_type_id": hospital_type.id,
            "asset_type_name": hospital_type.name,
            "lifecycle_template_id": bld_template.id,
            "current_stage": "OPERATIONAL",
            "location": AssetLocation(state="Gujarat", district="Ahmedabad", taluka="Asarwa", city="Ahmedabad", address="Civil Hospital Campus, Asarwa", latitude=23.0510, longitude=72.6030),
            "commissioned_date": date(2020, 1, 26),
            "responsibility": AssetResponsibility(custodian="R&B Capital Division", operator="Health & Family Welfare Dept", maintenance_agency="R&B Electrical & Civil Hospital Sub-division"),
            "current_condition_score": 84.0,
            "current_condition_rating": "GOOD",
            "current_risk_level": "LOW",
            "risk_score": 24.0,
            "next_action": "Quarterly HVAC & Fire Safety Audit",
            "next_action_due": date(2026, 12, 1),
            "next_action_priority": "LOW",
            "last_inspection_date": date(2025, 12, 5),
            "next_inspection_due": date(2026, 6, 5),
            "estimated_value": 32000.0,
            "replacement_value": 41500.0,
            "planned_lifecycle": PlannedLifecycle(design_life_years=60, expected_end_of_life=date(2080, 1, 26), initial_cost=31000.0),
        },
        {
            "code": "R&B-BRG-00004",
            "name": "Old Golden Bridge Over Narmada River, Bharuch",
            "description": "Historic 1881 iron girder bridge requiring stringent load limits and intensive monitoring.",
            "infrastructure_class_id": brg_class.id,
            "infrastructure_class_code": "BRIDGE",
            "asset_type_id": river_brg_type.id,
            "asset_type_name": river_brg_type.name,
            "lifecycle_template_id": brg_template.id,
            "current_stage": "SPECIAL_MONITORING",
            "location": AssetLocation(state="Gujarat", district="Bharuch", taluka="Bharuch", city="Bharuch", address="Connecting Bharuch to Ankleshwar", latitude=21.6980, longitude=72.9850),
            "commissioned_date": date(1881, 5, 16),
            "responsibility": AssetResponsibility(custodian="Roads & Buildings Department", operator="R&B Bridge Wing", maintenance_agency="R&B Bharuch Division"),
            "current_condition_score": 38.0,
            "current_condition_rating": "POOR",
            "current_risk_level": "CRITICAL",
            "risk_score": 88.0,
            "next_action": "Emergency Pier Scour Assessment & Pier Jacketing",
            "next_action_due": date(2026, 10, 5),
            "next_action_priority": "URGENT",
            "last_inspection_date": date(2026, 2, 20),
            "next_inspection_due": date(2026, 5, 20),
            "estimated_value": 12500.0,
            "replacement_value": 45000.0,
            "planned_lifecycle": PlannedLifecycle(design_life_years=100, expected_end_of_life=date(2028, 12, 31), initial_cost=500.0),
        },
        {
            "code": "R&B-RD-00005",
            "name": "Surat-Dumas Beach Expressway Link",
            "description": "18.5 km 4-lane divided urban arterial highway serving Surat airport and Dumas coastal belt.",
            "infrastructure_class_id": road_class.id,
            "infrastructure_class_code": "ROAD",
            "asset_type_id": sh_type.id,
            "asset_type_name": sh_type.name,
            "lifecycle_template_id": road_template.id,
            "current_stage": "OPERATIONAL",
            "location": AssetLocation(state="Gujarat", district="Surat", taluka="Choryasi", city="Surat", address="Surat Dumas Road", latitude=21.1450, longitude=72.7680),
            "commissioned_date": date(2021, 6, 10),
            "responsibility": AssetResponsibility(custodian="R&B Surat Division", operator="R&B Dept", maintenance_agency="Surat City R&B Sub-Division"),
            "current_condition_score": 79.0,
            "current_condition_rating": "GOOD",
            "current_risk_level": "LOW",
            "risk_score": 22.0,
            "next_action": "Monsoon Pre-checks and Storm Drain Cleaning",
            "next_action_due": date(2026, 11, 30),
            "next_action_priority": "LOW",
            "last_inspection_date": date(2026, 1, 5),
            "next_inspection_due": date(2026, 7, 5),
            "estimated_value": 16500.0,
            "replacement_value": 21000.0,
            "planned_lifecycle": PlannedLifecycle(design_life_years=20, expected_end_of_life=date(2041, 6, 10), initial_cost=15800.0),
        },
        {
            "code": "R&B-BLD-00006",
            "name": "Vadodara District Collectorate Complex (Kothi Compound)",
            "description": "Integrated administrative complex housing Revenue, Magistracy, Land Records and District Treasury.",
            "infrastructure_class_id": bld_class.id,
            "infrastructure_class_code": "BUILDING",
            "asset_type_id": collectorate_type.id,
            "asset_type_name": collectorate_type.name,
            "lifecycle_template_id": bld_template.id,
            "current_stage": "MAINTENANCE",
            "location": AssetLocation(state="Gujarat", district="Vadodara", taluka="Vadodara", city="Vadodara", address="Kothi Compound, Raopura", latitude=22.3020, longitude=73.1980),
            "commissioned_date": date(2008, 11, 14),
            "responsibility": AssetResponsibility(custodian="R&B Vadodara Circle", operator="Revenue Dept, Govt of Gujarat", maintenance_agency="Vadodara R&B Building Sub-division"),
            "current_condition_score": 58.0,
            "current_condition_rating": "FAIR",
            "current_risk_level": "MEDIUM",
            "risk_score": 48.0,
            "next_action": "Roof Waterproofing & Electrical Distribution Upgradation",
            "next_action_due": date(2026, 10, 15),
            "next_action_priority": "MEDIUM",
            "last_inspection_date": date(2025, 10, 18),
            "next_inspection_due": date(2026, 4, 18),
            "estimated_value": 11200.0,
            "replacement_value": 18500.0,
            "planned_lifecycle": PlannedLifecycle(design_life_years=50, expected_end_of_life=date(2058, 11, 14), initial_cost=9200.0),
        },
        {
            "code": "R&B-BRG-00007",
            "name": "Rajkot Jubilee Garden Overbridge",
            "description": "Pre-stressed concrete railway overbridge (ROB) carrying 45,000 PCU daily over western railway main line.",
            "infrastructure_class_id": brg_class.id,
            "infrastructure_class_code": "BRIDGE",
            "asset_type_id": flyover_type.id,
            "asset_type_name": flyover_type.name,
            "lifecycle_template_id": brg_template.id,
            "current_stage": "MAJOR_REHABILITATION",
            "location": AssetLocation(state="Gujarat", district="Rajkot", taluka="Rajkot", city="Rajkot", address="Jubilee Garden, Station Road", latitude=22.3005, longitude=70.8022),
            "commissioned_date": date(1996, 7, 20),
            "responsibility": AssetResponsibility(custodian="R&B Rajkot Circle", operator="Rajkot Municipal Corp / R&B", maintenance_agency="R&B Rajkot Bridge Sub-division"),
            "current_condition_score": 44.0,
            "current_condition_rating": "POOR",
            "current_risk_level": "HIGH",
            "risk_score": 72.0,
            "next_action": "Neoprene Bearing Replacement & Expansion Joint Rehabilitation",
            "next_action_due": date(2026, 10, 10),
            "next_action_priority": "HIGH",
            "last_inspection_date": date(2026, 2, 1),
            "next_inspection_due": date(2026, 5, 1),
            "estimated_value": 6800.0,
            "replacement_value": 14200.0,
            "planned_lifecycle": PlannedLifecycle(design_life_years=50, expected_end_of_life=date(2046, 7, 20), initial_cost=3800.0),
        },
        {
            "code": "R&B-RD-00008",
            "name": "Bhavnagar-Somnath Coastal Highway NH-51 Ext.",
            "description": "Strategic maritime and coastal pilgrim corridor connecting Alang Shipyard and Veraval.",
            "infrastructure_class_id": road_class.id,
            "infrastructure_class_code": "ROAD",
            "asset_type_id": sh_type.id,
            "asset_type_name": sh_type.name,
            "lifecycle_template_id": road_template.id,
            "current_stage": "OPERATIONAL",
            "location": AssetLocation(state="Gujarat", district="Bhavnagar", taluka="Talaja", city="Bhavnagar", address="Coastal Highway SH-6 / NH-51 Link", latitude=21.4500, longitude=72.0500),
            "commissioned_date": date(2018, 12, 1),
            "responsibility": AssetResponsibility(custodian="R&B Bhavnagar Division", operator="R&B Coastal Highway Wing", maintenance_agency="R&B Coastal Maintenance Cell"),
            "current_condition_score": 74.0,
            "current_condition_rating": "GOOD",
            "current_risk_level": "LOW",
            "risk_score": 26.0,
            "next_action": "Routine Shoulder Profiling & Line Marking",
            "next_action_due": date(2026, 12, 20),
            "next_action_priority": "LOW",
            "last_inspection_date": date(2025, 11, 28),
            "next_inspection_due": date(2026, 5, 28),
            "estimated_value": 38000.0,
            "replacement_value": 46000.0,
            "planned_lifecycle": PlannedLifecycle(design_life_years=25, expected_end_of_life=date(2043, 12, 1), initial_cost=34000.0),
        }
    ]

    saved_assets = []
    for adata in assets_data:
        asset = Asset(**adata)
        await asset.insert()
        saved_assets.append(asset)

        # Initial lifecycle event
        event = LifecycleEvent(
            asset_id=asset.id,
            from_stage="NONE",
            to_stage=asset.current_stage,
            performed_by="System Initializer",
            notes=f"Initial asset baseline recorded as {asset.current_stage}",
        )
        await event.insert()

    # 8. Seed Asset Components (Bridge Bearings, Deck Slabs, HVAC, Pavement)
    # Atal Bridge Components
    atal = saved_assets[0]
    await AssetComponent(asset_id=atal.id, name="Structural Steel Truss Girder", component_type="Superstructure", condition="EXCELLENT", condition_score=94.0, is_critical=True, installed_date=date(2022, 8, 1)).insert()
    await AssetComponent(asset_id=atal.id, name="Cable Stay Tensioners", component_type="Stay Cables", condition="EXCELLENT", condition_score=95.0, is_critical=True, installed_date=date(2022, 8, 1)).insert()
    await AssetComponent(asset_id=atal.id, name="Modular Deck Surface with Anti-skid Coating", component_type="Deck Slab", condition="GOOD", condition_score=88.0, is_critical=False, installed_date=date(2022, 8, 1)).insert()

    # Old Golden Bridge Components
    golden = saved_assets[3]
    await AssetComponent(asset_id=golden.id, name="Cast Iron Screw Piles & Piers", component_type="Substructure", condition="POOR", condition_score=34.0, is_critical=True, installed_date=date(1881, 5, 1)).insert()
    await AssetComponent(asset_id=golden.id, name="Wrought Iron Lattice Girders", component_type="Superstructure", condition="POOR", condition_score=40.0, is_critical=True, installed_date=date(1881, 5, 1)).insert()
    await AssetComponent(asset_id=golden.id, name="Steel Roller Bearings", component_type="Bearings", condition="CRITICAL", condition_score=28.0, is_critical=True, installed_date=date(1975, 4, 1)).insert()

    # SG Highway Components
    sg_road = saved_assets[1]
    await AssetComponent(asset_id=sg_road.id, name="Dense Bituminous Macadam (DBM) Base", component_type="Pavement Base", condition="GOOD", condition_score=75.0, is_critical=True, installed_date=date(2019, 3, 1)).insert()
    await AssetComponent(asset_id=sg_road.id, name="Bituminous Concrete (BC) Wearing Course", component_type="Wearing Course", condition="FAIR", condition_score=62.0, is_critical=False, installed_date=date(2019, 3, 1)).insert()
    await AssetComponent(asset_id=sg_road.id, name="RCC Storm Water Side Drainage Box", component_type="Drainage", condition="GOOD", condition_score=78.0, is_critical=False, installed_date=date(2019, 3, 1)).insert()

    # Civil Hospital Components
    civil_hosp = saved_assets[2]
    await AssetComponent(asset_id=civil_hosp.id, name="RCC Framed Earthquake-Resistant Core", component_type="Structure", condition="EXCELLENT", condition_score=92.0, is_critical=True, installed_date=date(2020, 1, 1)).insert()
    await AssetComponent(asset_id=civil_hosp.id, name="Central Chiller & HVAC Air Handling Units", component_type="MEP Services", condition="GOOD", condition_score=82.0, is_critical=True, installed_date=date(2020, 1, 1)).insert()
    await AssetComponent(asset_id=civil_hosp.id, name="Automated Fire Detection & Hydrant Grid", component_type="Safety Systems", condition="EXCELLENT", condition_score=90.0, is_critical=True, installed_date=date(2020, 1, 1)).insert()

    # 9. Seed Inspections & Historical Condition Assessments
    for asset in saved_assets:
        # Condition Assessment 1 year ago
        c1 = ConditionAssessment(
            asset_id=asset.id,
            assessment_date=date.today() - timedelta(days=360),
            overall_score=min(100.0, (asset.current_condition_score or 75.0) + 6.0),
            overall_rating="GOOD" if (asset.current_condition_score or 75.0) > 60 else "FAIR",
            structural_condition="GOOD",
            structural_score=min(100.0, (asset.current_condition_score or 75.0) + 8.0),
            functional_condition="GOOD",
            safety_condition="GOOD",
            inspector="Er. Amit Shah",
            findings="Previous annual baseline assessment completed.",
            recommendations="Continue scheduled maintenance cycles.",
        )
        await c1.insert()

        # Condition Assessment Recent
        c2 = ConditionAssessment(
            asset_id=asset.id,
            assessment_date=asset.last_inspection_date or (date.today() - timedelta(days=60)),
            overall_score=asset.current_condition_score or 70.0,
            overall_rating=asset.current_condition_rating,
            structural_condition=asset.current_condition_rating,
            structural_score=asset.current_condition_score,
            functional_condition=asset.current_condition_rating,
            safety_condition="GOOD" if asset.current_condition_rating != "CRITICAL" else "POOR",
            inspector="Smt. Priya Desai (QC Assistant Engineer)",
            findings=f"Latest comprehensive inspection conducted for {asset.name}. Structural integrity evaluated.",
            recommendations=asset.next_action,
        )
        await c2.insert()

        # Inspection Record
        insp = Inspection(
            asset_id=asset.id,
            inspection_type="ROUTINE" if asset.current_risk_level != "CRITICAL" else "SPECIAL",
            inspection_date=asset.last_inspection_date or (date.today() - timedelta(days=45)),
            inspector_name="Smt. Priya Desai",
            inspector_designation="AEE (Quality Control)",
            inspector_agency="Gujarat R&B Quality Control Wing",
            overall_condition=asset.current_condition_rating,
            condition_score=asset.current_condition_score,
            structural_condition=asset.current_condition_rating,
            functional_condition="GOOD" if asset.current_condition_rating in ["GOOD", "EXCELLENT"] else "FAIR",
            safety_condition="POOR" if asset.current_risk_level == "CRITICAL" else "GOOD",
            findings=f"Detailed on-site field evaluation completed for {asset.code}.",
            recommendations=asset.next_action,
            defects_found=["Minor surface weathering"] if asset.current_condition_rating != "CRITICAL" else ["Bearing freeze", "Deep scour around pier 4", "Vibration exceeding threshold"],
            next_inspection_date=asset.next_inspection_due,
            requires_immediate_action=True if asset.current_risk_level in ["CRITICAL", "HIGH"] else False,
            immediate_action_description="Deploy emergency retrofitting and restrict overload vehicles" if asset.current_risk_level == "CRITICAL" else "",
        )
        await insp.insert()

        # Risk Assessment Record
        await assess_risk_for_asset(
            asset=asset,
            criticality="HIGH" if asset.infrastructure_class_code == "BRIDGE" else "MEDIUM",
            safety_impact="CRITICAL" if asset.current_condition_rating == "POOR" else "LOW",
            service_impact="HIGH" if asset.infrastructure_class_code == "ROAD" else "MEDIUM",
        )

        # Maintenance Records
        m1 = MaintenanceRecord(
            asset_id=asset.id,
            maintenance_type="PREVENTIVE",
            title=f"Routine Annual Maintenance - {asset.code}",
            description="Routine structural tightening, joint cleaning, drain desilting.",
            priority="MEDIUM",
            status="COMPLETED",
            estimated_cost=25.0,
            actual_cost=22.4,
            scheduled_date=date(2025, 4, 1),
            start_date=date(2025, 4, 3),
            completion_date=date(2025, 4, 18),
            assigned_agency=asset.responsibility.maintenance_agency,
            performed_by="Gujarat State R&B Sub-Division Team",
            approved_by="Executive Engineer",
            work_done="Completed all preventive checks without observation.",
            condition_after=asset.current_condition_rating,
        )
        await m1.insert()

        if asset.current_risk_level in ["CRITICAL", "HIGH", "MEDIUM"]:
            m2 = MaintenanceRecord(
                asset_id=asset.id,
                maintenance_type="REHABILITATION" if asset.current_risk_level == "CRITICAL" else "CORRECTIVE",
                title=f"Action Plan: {asset.next_action}",
                description="Engineered intervention triggered by condition scoring and risk evaluation.",
                priority="URGENT" if asset.current_risk_level == "CRITICAL" else "HIGH",
                status="IN_PROGRESS" if asset.current_risk_level == "CRITICAL" else "SCHEDULED",
                estimated_cost=340.0 if asset.current_risk_level == "CRITICAL" else 65.0,
                scheduled_date=asset.next_action_due or (date.today() + timedelta(days=15)),
                assigned_agency=asset.responsibility.maintenance_agency,
            )
            await m2.insert()

        # Asset Costs
        await AssetCost(
            asset_id=asset.id,
            cost_type="CAPITAL",
            description="Original Construction & Handover Cost",
            amount=asset.estimated_value or 5000.0,
            financial_year="2021-2022",
            date_incurred=asset.commissioned_date,
            source_of_funds="Gujarat State R&B Capital Budget",
        ).insert()

        await AssetCost(
            asset_id=asset.id,
            cost_type="MAINTENANCE",
            description="Operational maintenance & inspection cycles",
            amount=round((asset.estimated_value or 5000.0) * 0.03, 2),
            financial_year="2025-2026",
            date_incurred=date(2025, 11, 15),
            source_of_funds="R&B Non-Plan O&M Grant",
        ).insert()

        # Attached Documents metadata
        await AssetDocument(
            asset_id=asset.id,
            title="As-Built Completion Drawings & Structural Design Sanction",
            document_type="DESIGN_DRAWING",
            description="Approved GA and structural drawings signed by Chief Engineer R&B.",
            file_name=f"{asset.code}_AsBuilt_Drawings.pdf",
            file_url=f"/documents/{asset.code}_AsBuilt_Drawings.pdf",
            uploaded_by="Er. Amit Shah",
        ).insert()

        await AssetDocument(
            asset_id=asset.id,
            title="Latest Quality Control Inspection Certificate",
            document_type="INSPECTION_REPORT",
            description="QC Wing structural audit findings and load rating assessment.",
            file_name=f"{asset.code}_QC_Inspection_2026.pdf",
            file_url=f"/documents/{asset.code}_QC_Inspection_2026.pdf",
            uploaded_by="Smt. Priya Desai",
        ).insert()

    # 10. Seed Sample Issues
    await Issue(
        asset_id=golden.id,
        title="Excessive vibration reported during heavy vehicle transit on Span 3",
        description="Public bus drivers noted pronounced deflection near Pier 4 screw pile assembly.",
        severity="CRITICAL",
        category="STRUCTURAL",
        reported_by="Bharuch Traffic Police & R&B Field Supervisor",
        status="OPEN",
    ).insert()

    await Issue(
        asset_id=sg_road.id,
        title="Bituminous bleeding and rutting observed near Vaishnodevi Circle",
        description="High ambient temperature and heavy axle loading caused 25mm rut depth.",
        severity="MEDIUM",
        category="PAVEMENT",
        reported_by="QC Inspection Patrol",
        status="OPEN",
    ).insert()

    print("[DONE] Successfully populated Gujarat R&B Lifecycle Platform demo dataset!")
    return {
        "status": "success",
        "message": "Gujarat R&B Database seeded successfully",
        "counts": {
            "users": 3,
            "classes": 3,
            "asset_types": 7,
            "lifecycle_templates": 3,
            "projects": len(project_objs),
            "assets": len(saved_assets),
        }
    }


@seed_router.post("/seed")
async def seed_database_endpoint():
    """Trigger complete re-seeding with realistic Gujarat R&B demo dataset."""
    return await run_seed()


if __name__ == "__main__":
    import asyncio
    from app.database import init_db, close_db

    async def _cli_seed():
        await init_db()
        await run_seed()
        await close_db()

    asyncio.run(_cli_seed())
