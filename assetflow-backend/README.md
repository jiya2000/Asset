# AssetFlow — Enterprise Asset Management System

## Architecture

AssetFlow is a **four-layer backend** built from scratch with **FastAPI + PostgreSQL + SQLAlchemy 2.0**. No ORM auto-admin, no Odoo modules — pure Python engineering.

```
┌──────────────────────────────┐
│     Presentation Layer       │  FastAPI routers & Pydantic schemas
│   (thin — no business logic) │  Validates HTTP input, returns JSON
├──────────────────────────────┤
│     Business Services        │  Workflow orchestration
│  (allocation, maintenance,   │  Calls validators, then repos
│   dashboard)                 │  Logs every action to activity trail
├──────────────────────────────┤
│     Validation Layer         │  Pure rule checks
│  (allocation_rules,          │  Raises 409 Conflict on violations
│   maintenance_rules)         │  No DB writes — stateless functions
├──────────────────────────────┤
│     Repository Layer         │  SQL access only
│  (asset_repo, allocation_    │  CRUD, search, aggregations
│   repo, activity_repo)       │  No business rules here
├──────────────────────────────┤
│     PostgreSQL               │  Normalized relational schema
│  (7 tables, proper FKs,      │  Enums, indexes, constraints
│   audit timestamps)          │
└──────────────────────────────┘
```

## Why This Architecture?

| Decision | Rationale |
|----------|-----------|
| **4-layer separation** | Routers stay thin (testable), business logic is isolated (swappable), validators are pure functions (unit-testable without DB), repos hide SQL details |
| **Enum-based RBAC** | Simple 3-role model (Admin/Manager/Employee) — no over-engineered join tables for a fixed role set |
| **Soft deletes** | `is_active` flag preserves FK integrity and audit trails — never physically delete a row |
| **Transfer as separate entity** | Links old and new allocation IDs — preserves full audit chain instead of mutating allocation rows |
| **Activity log** | Append-only table for immutable audit trail — every allocation, transfer, and maintenance action is logged |
| **Smart insights** | Dashboard queries detect overdue returns, expiring warranties, and high-maintenance assets proactively |

## Database Schema

### Tables (7)
1. **departments** — organizational units (code, name)
2. **employees** — users with RBAC roles, FK to department
3. **categories** — runtime-extensible asset categories
4. **assets** — core entity with status state machine, condition, purchase/warranty tracking
5. **allocations** — lifecycle: Pending → Approved → Active → Returned
6. **transfers** — links two allocations (from/to), approval workflow
7. **maintenance_requests** — Pending → Approved → In_Progress → Resolved
8. **activity_logs** — immutable audit trail

### Key Relationships
- Asset ← many → Allocations (1:N)
- Asset ← many → MaintenanceRequests (1:N)
- Allocation → Employee (assigned to)
- Allocation → Employee (approved by)
- Transfer → from_allocation, to_allocation
- Employee → Department (N:1)
- Asset → Category (N:1)

## API Endpoints

### Auth (`/api/auth`)
- `POST /signup` — Register new employee
- `POST /login` — JWT token
- `GET /me` — Current user profile
- `GET /employees` — Employee directory
- `POST /departments` — Create department (Admin)

### Assets (`/api/assets`)
- `POST /` — Register asset (Admin/Manager)
- `GET /` — Search/filter with pagination
- `GET /{id}` — Asset detail
- `PATCH /{id}` — Update asset
- `DELETE /{id}` — Soft delete (Admin)
- `POST /categories` — Create category
- `GET /categories` — List categories

### Allocations (`/api/allocations`)
- `POST /` — Request allocation
- `GET /` — List all (with status filter)
- `GET /pending` — Approval center
- `POST /{id}/approve` — Approve allocation
- `POST /{id}/return` — Return asset
- `POST /transfers` — Initiate transfer
- `POST /transfers/{id}/approve` — Approve transfer

### Maintenance (`/api/maintenance`)
- `POST /` — Create request (any user)
- `GET /` — List all
- `POST /{id}/approve` — Approve (Admin/Manager)
- `POST /{id}/start` — Begin work
- `POST /{id}/resolve` — Mark resolved

### Dashboard (`/api/dashboard`)
- `GET /kpis` — Aggregated metrics
- `GET /insights` — Smart proactive alerts
- `GET /activity` — Recent activity feed
- `GET /timeline/{asset_id}` — Per-asset history

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up PostgreSQL database
createdb assetflow

# 3. Configure environment
cp .env.example .env
# edit .env with your DB credentials

# 4. Run migrations (or let seed_data create tables)
alembic upgrade head

# 5. Seed demo data
python seed_data.py

# 6. Start the server
uvicorn app.main:app --reload --port 8000

# 7. Open API docs
# http://localhost:8000/docs
```

## Demo Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | arjun.sharma@assetflow.com | password123 |
| Manager | priya.patel@assetflow.com | password123 |
| Employee | rahul.kumar@assetflow.com | password123 |

## Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Architecture**: 4-layer (Presentation → Service → Validator → Repository)
