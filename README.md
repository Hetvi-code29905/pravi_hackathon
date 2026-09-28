# 🏛️ PRAVI — Digital Infrastructure Lifecycle & Asset Management Platform
### Roads & Buildings Department · Government of Gujarat

![Status](https://img.shields.io/badge/Status-Operational-10b981?style=for-the-badge)
![Compliance](https://img.shields.io/badge/Compliance-IRC%3ASP%3A35%20%7C%20CPWD%20%7C%20PIARC-0ea5e9?style=for-the-badge)
![GIS](https://img.shields.io/badge/GIS-Spatial%20Mapping%20(Gujarat)-f59e0b?style=for-the-badge)

**PRAVI R&B** is an enterprise infrastructure lifecycle management engine built for the **Roads & Buildings Department, Government of Gujarat**. It unifies the temporary capital project lifecycle (`PLANNING` → `DESIGN` → `TENDER` → `CONSTRUCTION` → `COMMISSIONING`) with permanent operational **Physical Asset Passports** (`OPERATIONAL` → `PREVENTIVE_MAINTENANCE` → `REHABILITATION` → `DECOMMISSIONED`) using state-wide GIS spatial mapping.

---

## 🌟 Key Features

1. **Interactive GIS Gujarat Spatial Command Map:**
   - Real-time mapping across 33 Districts and major State Corridors (SH-41, SG Highway, NH-48 Feeder, AIIMS Access Corridor).
   - Dynamic condition-coded pins (Excellent, Good, Fair, Poor, Critical) with instant Asset Passport inspector drawers.
2. **Actionable Step-by-Step Lifecycle Progression:**
   - Real civil engineering review items (Planning clearances, structural milestone tests, emergency rehabilitation requisitions).
   - Role-gated **Accept** and **Reject** review desk directly advancing stages in MongoDB.
3. **Automated Capital Handover Engine:**
   - Converts completed construction projects directly into persistent Physical Asset Passports with QR/Barcode generation, maintenance schedules, and initial lifecycle events.
4. **180-Day Structural Health Audits & O&M Work Orders:**
   - Pavement Condition Index (PCI) and Bridge Health Index tracking with ultrasonic pulse velocity / distress monitoring.
5. **Obsidian SaaS UI/UX:**
   - Glassmorphism design tokens, real-time notification toast center, and live Mongo sync pulse indicators.

---

## 🔐 Stakeholder Roles & Pre-Seeded Credentials

The platform features fine-grained Role-Based Access Control (RBAC) with tailored command centers for each stakeholder:

| Stakeholder Role | Name & Title | Official Email (Username) | Password | Key Actionable Authority & Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **SECRETARY** | Shri M. K. Das, IAS *(Principal Secretary)* | `secretary@rnb.gujarat.gov.in` | `secretary123` | **State Cabinet Authority:** Approve Planning Clearances, Sanction Project Handover to Live Assets, Authorize Emergency Rehabilitation Funds (₹ Cr). |
| **ADMIN** | Shri Rajesh Patel *(Chief Engineer & State Asset Director)* | `admin@rnb.gujarat.gov.in` | `admin123` | **Platform Governance:** State registry administration, GIS spatial sync, user management, and MongoDB lifecycle state machine configuration. |
| **ENGINEER** | Er. Amit Shah *(Executive Engineer)* | `engineer@rnb.gujarat.gov.in` | `engineer123` | **Technical Supervision:** Verify EPC contractor construction milestones (e.g. M45 Concrete Core strength), advance project stages, and dispatch maintenance work orders. |
| **INSPECTOR** | Smt. Priya Desai *(QC Assistant Executive Engineer)* | `inspector@rnb.gujarat.gov.in` | `inspector123` | **Quality & Safety Compliance:** Conduct 180-day structural condition audits, log distress & crack defect notices, calculate Bridge Health / Pavement Condition Index (PCI). |
| **CONTRACTOR** | M/s L&T Infrastructure *(EPC Concessionaire Partner)* | `contractor@rnb.gujarat.gov.in` | `contractor123` | **Milestone Delivery:** Execute capital packages, submit physical milestone completion dossiers, and upload quality test certificates for review. |

---

## 🛠️ Technology Stack

* **Backend:** Python 3.10+, FastAPI, Beanie ODM, Motor (Async MongoDB), Pydantic v2, PyJWT, Passlib (Bcrypt).
* **Frontend:** React 19, Vite, Leaflet.js, React-Leaflet, Vanilla CSS Design System (Glassmorphism), Plus Jakarta Sans & Outfit typography.
* **Database:** MongoDB (`mongodb://localhost:27017/rnb_lifecycle_platform`).

---

## ⚡ Quick Start & Local Setup

### 1. Backend Setup
```bash
cd backend
# Create and activate virtual environment
python -m venv pravy
.\pravy\Scripts\activate   # On Windows
# source pravy/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Seed Realistic Gujarat Demo Dataset
* Click **"Reset Demo Data"** directly inside the app top navigation bar, or run:
```bash
cd backend
python -m app.seeds.seed_data
python ensure_users.py
```

---

## 📜 Compliance Standards
* **IRC:SP:35** — Guidelines for Inspection and Maintenance of Bridge Structures
* **CPWD Maintenance Manual 2023** — Government of India Public Works Standards
* **PIARC Asset Management Guide** — World Road Association Lifecycles
