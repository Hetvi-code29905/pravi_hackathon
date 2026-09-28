# 🏛️ PRAVI R&B — System Architecture & Workflow Specifications
### Roads & Buildings Department · Government of Gujarat

This document provides a comprehensive technical overview of the **PRAVI** (Gujarat Digital Infrastructure Lifecycle & GIS Asset Management Engine) architecture, component interactions, data pipelines, and role-based authority models.

---

## 1. High-Level 3-Tier Enterprise Architecture

```mermaid
graph TB
    subgraph "CLIENT TIER (Frontend SaaS Portal - React 19 + Vite)"
        UI_AUTH["🔐 Authentication & Role Switcher<br/>(JWT + Session Context)"]
        UI_DASH["📊 Executive Command Center<br/>(KPIs & Real-time Action Desk)"]
        UI_GIS["🗺️ Interactive Gujarat GIS Map<br/>(Leaflet.js + 33 Districts Layer)"]
        UI_PASSPORT["📘 Digital Asset Passports<br/>(Components, Timeline, Documents)"]
        UI_PIPELINE["🏗️ Capital Projects Pipeline<br/>(Stage Stepper & Handover Modal)"]
        UI_OPS["🔧 Field Operations & Inspections<br/>(Work Orders & Defect Log)"]
        UI_NOTIF["🔔 Real-time Toast & Activity Center<br/>(NotificationProvider)"]
    end

    subgraph "API & APPLICATION TIER (FastAPI Backend Engine)"
        ROUTER_AUTH["/api/auth<br/>(Login, Register, RBAC)"]
        ROUTER_DASH["/api/dashboard<br/>(GIS Assets & State KPIs)"]
        ROUTER_PRJ["/api/projects<br/>(Lifecycle Review & Handover)"]
        ROUTER_AST["/api/assets<br/>(Asset Passports & Timelines)"]
        ROUTER_OPS["/api/operations<br/>(Inspections, Work Orders, Issues)"]
        ROUTER_INFRA["/api/infrastructure<br/>(Classes: Building, Road, Bridge)"]

        subgraph "Core Business Logic Engines"
            ENGINE_LC["⚙️ Lifecycle State Machine<br/>(Transitions & Approvals)"]
            ENGINE_RISK["🛡️ Risk Calculation Engine<br/>(PCI, Scour Risk, Health Score)"]
            ENGINE_HANDOVER["✨ Project-to-Asset Converter<br/>(Asset Code, QR, Custodian)"]
        end
    end

    subgraph "PERSISTENCE TIER (MongoDB + Beanie ODM)"
        DB_USERS[("👤 users Collection")]
        DB_PROJECTS[("🏗️ projects Collection")]
        DB_ASSETS[("📘 assets Collection")]
        DB_TEMPLATES[("📋 lifecycle_templates")]
        DB_EVENTS[("📜 lifecycle_events (Audit Trail)")]
        DB_INSPECTIONS[("🔍 inspections Collection")]
        DB_MAINTENANCE[("🔧 maintenance_records")]
        DB_ISSUES[("⚠️ issues Collection")]
        DB_CLASSES[("🏛️ infrastructure_classes")]
    end

    %% Client to API Connections
    UI_AUTH --> ROUTER_AUTH
    UI_DASH --> ROUTER_DASH
    UI_GIS --> ROUTER_DASH
    UI_PIPELINE --> ROUTER_PRJ
    UI_PASSPORT --> ROUTER_AST
    UI_OPS --> ROUTER_OPS

    %% API to Business Engines
    ROUTER_PRJ --> ENGINE_LC
    ROUTER_PRJ --> ENGINE_HANDOVER
    ROUTER_AST --> ENGINE_RISK
    ROUTER_OPS --> ENGINE_LC

    %% Engines to Database
    ROUTER_AUTH --> DB_USERS
    ROUTER_DASH --> DB_ASSETS
    ROUTER_DASH --> DB_PROJECTS
    ENGINE_LC --> DB_PROJECTS
    ENGINE_LC --> DB_EVENTS
    ENGINE_HANDOVER --> DB_ASSETS
    ROUTER_AST --> DB_ASSETS
    ROUTER_OPS --> DB_INSPECTIONS
    ROUTER_OPS --> DB_MAINTENANCE
    ROUTER_OPS --> DB_ISSUES
    ROUTER_INFRA --> DB_CLASSES
    ENGINE_LC --> DB_TEMPLATES
```

---

## 2. Infrastructure Lifecycle State Machine Workflow

PRAVI bridges the gap between the **temporary construction lifecycle** and the **permanent operational asset lifecycle**:

```mermaid
stateDiagram-v2
    [*] --> NEED: Identification / Public Need
    NEED --> PLANNING: Preliminary Survey (EPC)
    PLANNING --> DESIGN: Cabinet Clearance Approved
    DESIGN --> TENDER: Detailed Project Report (DPR)
    TENDER --> CONSTRUCTION: Tender Awarded to Contractor
    CONSTRUCTION --> QUALITY_ACCEPTANCE: Milestone Verification (Concrete/Subgrade)
    QUALITY_ACCEPTANCE --> COMMISSIONING: 100% Quality Signoff
    COMMISSIONING --> HANDOVER: Executive Sanction Granted

    state "PHYSICAL ASSET PASSPORT CREATED" as AssetLifecycle {
        HANDOVER --> OPERATIONAL: Live Mongo Registry & Geo-Tagged
        OPERATIONAL --> PREVENTIVE_MAINTENANCE: 180-Day Inspection Cycle
        PREVENTIVE_MAINTENANCE --> OPERATIONAL: Work Order Completed
        OPERATIONAL --> REHABILITATION: Critical Distress / Low PCI (<60)
        REHABILITATION --> OPERATIONAL: Remedial Works Certified
        REHABILITATION --> DECOMMISSIONED: End of Service Life (IRC Standards)
    }

    DECOMMISSIONED --> [*]
```

---

## 3. Stakeholder Authority Matrix (Role-Based Access Control)

```mermaid
flowchart TD
    subgraph "ROLE ACCESS MATRIX"
        SEC["👤 PRINCIPAL SECRETARY (IAS)<br/>• Cabinet Sanctions<br/>• Handover Approvals<br/>• Capex Fund Disbursements"]
        ENG["👤 EXECUTIVE ENGINEER<br/>• Construction Milestones<br/>• Quality Verification<br/>• Work Order Dispatch"]
        INS["👤 QUALITY AUDITOR (QC)<br/>• 180-Day Condition Audits<br/>• PCI & Health Scoring<br/>• Defect Notices"]
        CON["👤 EPC CONTRACTOR<br/>• Milestone Submissions<br/>• Test Dossier Uploads<br/>• Package Execution"]
        ADM["👤 STATE ADMIN (Chief Engineer)<br/>• System Governance<br/>• GIS Spatial Layer Sync<br/>• Lifecycle State Rules"]
    end

    subgraph "ACTIONABLE LIFECYCLE REVIEW DESK"
        REV_CLEARANCE{"Clearance Review<br/>(Planning Stage)"}
        REV_MILESTONE{"Milestone Review<br/>(Construction Stage)"}
        REV_HANDOVER{"Handover Sanction<br/>(Commissioning)"}
        REV_REHAB{"Rehab Sanction<br/>(Operational Distress)"}
    end

    SEC -->|Accept / Reject| REV_CLEARANCE
    SEC -->|Accept / Reject| REV_HANDOVER
    SEC -->|Accept / Reject| REV_REHAB

    ENG -->|Accept / Reject| REV_MILESTONE
    ENG -->|Verify Handover| REV_HANDOVER

    INS -->|Audit Defect Log| REV_REHAB
    INS -->|Quality Signoff| REV_MILESTONE

    CON -->|Submit Dossier| REV_MILESTONE
    ADM -->|System Override| REV_HANDOVER
```

---

## 4. Automated Project-to-Asset Handover Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Secretary as Principal Secretary (R&B)
    participant UI as Frontend Dashboard
    participant API as FastAPI Backend (/api/projects)
    participant Engine as Handover & Lifecycle Engine
    participant DB as MongoDB Atlas / Local

    Secretary->>UI: Clicks "Grant Handover Sanction & Create Asset"
    UI->>API: POST /api/projects/{id}/review { action: HANDOVER_SANCTION, decision: ACCEPTED }
    API->>API: Validate Role = SECRETARY / ADMIN
    API->>Engine: Generate Unique Asset Code (e.g. R&B-BRG-00004)
    Engine->>DB: Insert new Asset document (current_stage="OPERATIONAL", PCI=100)
    Engine->>DB: Record immutable LifecycleEvent (Performed by Shri M. K. Das, IAS)
    Engine->>DB: Update Project document (status="HANDOVER", linked_asset_id=asset.id)
    DB-->>API: Success Response with Asset Passport Details
    API-->>UI: 200 OK + Asset Passport Data
    UI->>UI: Trigger Real-time Toast & Update GIS Map Pins
```

---

## 5. GIS Spatial Infrastructure Data Model

```mermaid
classDiagram
    class InfrastructureClass {
        +String id
        +String code (BUILDING | ROAD | BRIDGE)
        +String name
        +String color
        +Boolean is_active
    }

    class Project {
        +String id
        +String code (PRJ-RNB-2026-XXXX)
        +String name
        +String status (NEED..HANDOVER)
        +Float estimated_cost
        +Float sanctioned_cost
        +ProjectLocation location
        +String contractor
        +String supervising_officer
        +String asset_id
    }

    class Asset {
        +String id
        +String code (R&B-RD-XXXXX)
        +String name
        +String current_stage (OPERATIONAL..)
        +AssetLocation location (Lat, Long, District, Taluka)
        +AssetResponsibility responsibility
        +Float estimated_value
        +Float current_condition_score (PCI)
        +String current_condition_rating
        +String current_risk_level
    }

    class LifecycleEvent {
        +String id
        +String asset_id
        +String from_stage
        +String to_stage
        +DateTime transition_date
        +String performed_by
        +String notes
    }

    InfrastructureClass "1" <-- "*" Project : classifies
    Project "1" --> "1" Asset : converts to
    Asset "1" --> "*" LifecycleEvent : logs history
```
