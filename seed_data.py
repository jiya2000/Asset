"""
Realistic seed data for demo.

Creates:
  - 5 departments (Engineering, HR, Finance, Marketing, Operations)
  - 1 admin + 1 manager + 8 employees across departments
  - 5 asset categories (Laptops, Monitors, Phones, Accessories, Furniture)
  - 15 assets with realistic names, tags, serial numbers, purchase info
  - Demo scenarios:
    • A laptop currently allocated (active)
    • A laptop mid-transfer (pending transfer)
    • One overdue return
    • One asset under maintenance
    • Several available assets ready for allocation

Run:  python seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone, timedelta, date
from app.database import engine, SessionLocal, Base
from app.models.user import Employee, Department, RoleEnum
from app.models.asset import Asset, Category, AssetStatus, AssetCondition
from app.models.allocation import Allocation, Transfer, AllocationStatus, TransferStatus
from app.models.maintenance import MaintenanceRequest, MaintenancePriority, MaintenanceStatus
from app.models.activity_log import ActivityLog
from app.core.security import hash_password


def seed():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ── Check if already seeded ──
        if db.query(Department).first():
            print("⚠️  Database already seeded. Drop tables first to re-seed.")
            return

        print("🌱 Seeding AssetFlow database...")

        # ── Departments ───────────────────────────────────────────────
        departments = [
            Department(name="Engineering", code="ENG", description="Software & Hardware Engineering"),
            Department(name="Human Resources", code="HR", description="People operations and recruiting"),
            Department(name="Finance", code="FIN", description="Accounting and financial planning"),
            Department(name="Marketing", code="MKT", description="Brand, content, and growth"),
            Department(name="Operations", code="OPS", description="Facilities, logistics, and IT ops"),
        ]
        db.add_all(departments)
        db.flush()
        print(f"  ✅ {len(departments)} departments created")

        # ── Employees ─────────────────────────────────────────────────
        password = hash_password("password123")
        employees = [
            # Admin
            Employee(emp_code="EMP-001", first_name="Arjun", last_name="Sharma",
                     email="arjun.sharma@assetflow.com", hashed_password=password,
                     phone="+91-9876543210", role=RoleEnum.ADMIN,
                     department_id=departments[4].id),
            # Manager
            Employee(emp_code="EMP-002", first_name="Priya", last_name="Patel",
                     email="priya.patel@assetflow.com", hashed_password=password,
                     phone="+91-9876543211", role=RoleEnum.MANAGER,
                     department_id=departments[0].id),
            # Employees
            Employee(emp_code="EMP-003", first_name="Rahul", last_name="Kumar",
                     email="rahul.kumar@assetflow.com", hashed_password=password,
                     department_id=departments[0].id),
            Employee(emp_code="EMP-004", first_name="Sneha", last_name="Reddy",
                     email="sneha.reddy@assetflow.com", hashed_password=password,
                     department_id=departments[0].id),
            Employee(emp_code="EMP-005", first_name="Vikram", last_name="Singh",
                     email="vikram.singh@assetflow.com", hashed_password=password,
                     department_id=departments[1].id),
            Employee(emp_code="EMP-006", first_name="Anjali", last_name="Nair",
                     email="anjali.nair@assetflow.com", hashed_password=password,
                     department_id=departments[2].id),
            Employee(emp_code="EMP-007", first_name="Karthik", last_name="Iyer",
                     email="karthik.iyer@assetflow.com", hashed_password=password,
                     department_id=departments[3].id),
            Employee(emp_code="EMP-008", first_name="Meera", last_name="Gupta",
                     email="meera.gupta@assetflow.com", hashed_password=password,
                     department_id=departments[3].id),
            Employee(emp_code="EMP-009", first_name="Aditya", last_name="Joshi",
                     email="aditya.joshi@assetflow.com", hashed_password=password,
                     department_id=departments[4].id),
            Employee(emp_code="EMP-010", first_name="Divya", last_name="Menon",
                     email="divya.menon@assetflow.com", hashed_password=password,
                     department_id=departments[2].id),
        ]
        db.add_all(employees)
        db.flush()
        print(f"  ✅ {len(employees)} employees created (admin: arjun.sharma@assetflow.com / password123)")

        # ── Categories ────────────────────────────────────────────────
        categories = [
            Category(name="Laptops", code="LAP", description="Laptop computers and notebooks"),
            Category(name="Monitors", code="MON", description="External displays and monitors"),
            Category(name="Mobile Phones", code="PHN", description="Smartphones and mobile devices"),
            Category(name="Accessories", code="ACC", description="Keyboards, mice, headsets, etc."),
            Category(name="Furniture", code="FUR", description="Desks, chairs, and office furniture"),
        ]
        db.add_all(categories)
        db.flush()
        print(f"  ✅ {len(categories)} categories created")

        # ── Assets ────────────────────────────────────────────────────
        now = datetime.now(timezone.utc)
        assets = [
            # Laptops
            Asset(asset_tag="AST-LAP-001", name="MacBook Pro 16\" M3 Max",
                  serial_number="C02ZN1ABCD01", category_id=categories[0].id,
                  status=AssetStatus.ALLOCATED, condition=AssetCondition.GOOD,
                  purchase_date=date(2024, 3, 15), purchase_cost=249999.00,
                  warranty_expiry=date(2027, 3, 15), location="Building A",
                  department_id=departments[0].id),
            Asset(asset_tag="AST-LAP-002", name="Dell XPS 15",
                  serial_number="DELL9520XPS02", category_id=categories[0].id,
                  status=AssetStatus.ALLOCATED, condition=AssetCondition.GOOD,
                  purchase_date=date(2024, 6, 1), purchase_cost=189999.00,
                  warranty_expiry=date(2026, 8, 1), location="Building A",
                  department_id=departments[0].id),
            Asset(asset_tag="AST-LAP-003", name="ThinkPad X1 Carbon Gen 11",
                  serial_number="LENX1C11G303", category_id=categories[0].id,
                  status=AssetStatus.AVAILABLE, condition=AssetCondition.NEW,
                  purchase_date=date(2025, 1, 10), purchase_cost=164999.00,
                  warranty_expiry=date(2028, 1, 10), location="IT Store",
                  department_id=departments[4].id),
            Asset(asset_tag="AST-LAP-004", name="MacBook Air M2",
                  serial_number="C02AIR2M204", category_id=categories[0].id,
                  status=AssetStatus.UNDER_MAINTENANCE, condition=AssetCondition.FAIR,
                  purchase_date=date(2023, 9, 20), purchase_cost=129999.00,
                  warranty_expiry=date(2026, 9, 20), location="Repair Center",
                  department_id=departments[1].id),
            Asset(asset_tag="AST-LAP-005", name="HP EliteBook 850 G10",
                  serial_number="HPEB850G1005", category_id=categories[0].id,
                  status=AssetStatus.AVAILABLE, condition=AssetCondition.NEW,
                  purchase_date=date(2025, 5, 1), purchase_cost=139999.00,
                  warranty_expiry=date(2028, 5, 1), location="IT Store",
                  department_id=departments[4].id),
            # Monitors
            Asset(asset_tag="AST-MON-001", name="LG UltraFine 27\" 5K",
                  serial_number="LG5K27UF06", category_id=categories[1].id,
                  status=AssetStatus.ALLOCATED, condition=AssetCondition.GOOD,
                  purchase_date=date(2024, 4, 10), purchase_cost=54999.00,
                  warranty_expiry=date(2027, 4, 10), location="Building A",
                  department_id=departments[0].id),
            Asset(asset_tag="AST-MON-002", name="Dell UltraSharp 32\" 4K",
                  serial_number="DELU32K407", category_id=categories[1].id,
                  status=AssetStatus.AVAILABLE, condition=AssetCondition.GOOD,
                  purchase_date=date(2024, 7, 15), purchase_cost=45999.00,
                  warranty_expiry=date(2027, 7, 15), location="IT Store"),
            # Phones
            Asset(asset_tag="AST-PHN-001", name="iPhone 15 Pro",
                  serial_number="APIP15PRO08", category_id=categories[2].id,
                  status=AssetStatus.ALLOCATED, condition=AssetCondition.GOOD,
                  purchase_date=date(2024, 10, 1), purchase_cost=134900.00,
                  warranty_expiry=date(2025, 10, 1), location="Building A",
                  department_id=departments[3].id),
            Asset(asset_tag="AST-PHN-002", name="Samsung Galaxy S24 Ultra",
                  serial_number="SGS24U0009", category_id=categories[2].id,
                  status=AssetStatus.AVAILABLE, condition=AssetCondition.NEW,
                  purchase_date=date(2025, 2, 14), purchase_cost=129999.00,
                  warranty_expiry=date(2027, 2, 14), location="IT Store"),
            # Accessories
            Asset(asset_tag="AST-ACC-001", name="Logitech MX Master 3S",
                  serial_number="LOGMX3S0010", category_id=categories[3].id,
                  status=AssetStatus.ALLOCATED, condition=AssetCondition.GOOD,
                  purchase_date=date(2024, 5, 20), purchase_cost=8995.00,
                  location="Building A", department_id=departments[0].id),
            Asset(asset_tag="AST-ACC-002", name="Sony WH-1000XM5 Headphones",
                  serial_number="SNYWH5XM011", category_id=categories[3].id,
                  status=AssetStatus.AVAILABLE, condition=AssetCondition.NEW,
                  purchase_date=date(2025, 3, 1), purchase_cost=24990.00,
                  location="IT Store"),
            Asset(asset_tag="AST-ACC-003", name="Apple Magic Keyboard",
                  serial_number="APMGKB0012", category_id=categories[3].id,
                  status=AssetStatus.AVAILABLE, condition=AssetCondition.GOOD,
                  purchase_date=date(2024, 8, 15), purchase_cost=12900.00,
                  location="IT Store"),
            # Furniture
            Asset(asset_tag="AST-FUR-001", name="Herman Miller Aeron Chair",
                  serial_number="HMAERON013", category_id=categories[4].id,
                  status=AssetStatus.ALLOCATED, condition=AssetCondition.GOOD,
                  purchase_date=date(2023, 1, 15), purchase_cost=89999.00,
                  location="Building A, Floor 3", department_id=departments[0].id),
            Asset(asset_tag="AST-FUR-002", name="FlexiSpot Standing Desk E7",
                  serial_number="FSDE7014", category_id=categories[4].id,
                  status=AssetStatus.AVAILABLE, condition=AssetCondition.NEW,
                  purchase_date=date(2025, 4, 1), purchase_cost=34999.00,
                  location="Warehouse"),
            Asset(asset_tag="AST-FUR-003", name="Steelcase Leap V2 Chair",
                  serial_number="SCLV2015", category_id=categories[4].id,
                  status=AssetStatus.RETIRED, condition=AssetCondition.POOR,
                  purchase_date=date(2019, 6, 1), purchase_cost=65000.00,
                  location="Disposed"),
        ]
        db.add_all(assets)
        db.flush()
        print(f"  ✅ {len(assets)} assets created")

        # ── Allocations ───────────────────────────────────────────────
        alloc_time = now - timedelta(days=30)
        allocations = [
            # MacBook Pro → Rahul (active, will be overdue)
            Allocation(asset_id=assets[0].id, employee_id=employees[2].id,
                       status=AllocationStatus.ACTIVE,
                       allocated_at=alloc_time,
                       expected_return=now - timedelta(days=5),  # overdue!
                       purpose="Primary development machine",
                       approved_by=employees[1].id, approved_at=alloc_time),
            # Dell XPS → Sneha (active, mid-transfer pending)
            Allocation(asset_id=assets[1].id, employee_id=employees[3].id,
                       status=AllocationStatus.ACTIVE,
                       allocated_at=alloc_time - timedelta(days=10),
                       expected_return=now + timedelta(days=60),
                       purpose="QA testing workstation",
                       approved_by=employees[1].id,
                       approved_at=alloc_time - timedelta(days=10)),
            # LG Monitor → Rahul (active)
            Allocation(asset_id=assets[5].id, employee_id=employees[2].id,
                       status=AllocationStatus.ACTIVE,
                       allocated_at=alloc_time,
                       purpose="External display for dev work",
                       approved_by=employees[1].id, approved_at=alloc_time),
            # iPhone → Karthik (active)
            Allocation(asset_id=assets[7].id, employee_id=employees[6].id,
                       status=AllocationStatus.ACTIVE,
                       allocated_at=alloc_time - timedelta(days=20),
                       purpose="Business phone for client calls",
                       approved_by=employees[0].id,
                       approved_at=alloc_time - timedelta(days=20)),
            # MX Master → Rahul (active)
            Allocation(asset_id=assets[9].id, employee_id=employees[2].id,
                       status=AllocationStatus.ACTIVE,
                       allocated_at=alloc_time,
                       purpose="Ergonomic mouse",
                       approved_by=employees[1].id, approved_at=alloc_time),
            # Aeron Chair → Priya (active)
            Allocation(asset_id=assets[12].id, employee_id=employees[1].id,
                       status=AllocationStatus.ACTIVE,
                       allocated_at=now - timedelta(days=180),
                       purpose="Office seating",
                       approved_by=employees[0].id,
                       approved_at=now - timedelta(days=180)),
        ]
        db.add_all(allocations)
        db.flush()
        print(f"  ✅ {len(allocations)} allocations created (1 overdue)")

        # ── Transfer: Dell XPS from Sneha → Vikram (pending) ──────────
        transfer = Transfer(
            asset_id=assets[1].id,
            from_employee_id=employees[3].id,
            to_employee_id=employees[4].id,
            from_allocation_id=allocations[1].id,
            status=TransferStatus.PENDING,
            reason="Sneha moving to remote; Vikram needs workstation in office",
        )
        db.add(transfer)
        db.flush()
        print("  ✅ 1 pending transfer created (Dell XPS: Sneha → Vikram)")

        # ── Maintenance: MacBook Air under repair ─────────────────────
        maint = MaintenanceRequest(
            asset_id=assets[3].id,
            requested_by=employees[4].id,
            title="Battery swollen — needs replacement",
            description="MacBook Air battery is bulging, trackpad unresponsive. Sent to Apple authorized service.",
            priority=MaintenancePriority.HIGH,
            status=MaintenanceStatus.APPROVED,
            approved_by=employees[0].id,
            approved_at=now - timedelta(days=3),
        )
        db.add(maint)
        db.flush()
        print("  ✅ 1 maintenance request created (MacBook Air — battery replacement)")

        # ── Activity log entries ──────────────────────────────────────
        activities = [
            ActivityLog(action="EMPLOYEE_REGISTERED", entity_type="employee",
                        entity_id=employees[0].id, performed_by=employees[0].id,
                        description="Admin account created"),
            ActivityLog(action="ASSET_REGISTERED", entity_type="asset",
                        entity_id=assets[0].id, performed_by=employees[0].id,
                        description="MacBook Pro 16\" registered"),
            ActivityLog(action="ALLOCATION_APPROVED", entity_type="allocation",
                        entity_id=allocations[0].id, performed_by=employees[1].id,
                        description="MacBook Pro allocated to Rahul Kumar"),
            ActivityLog(action="TRANSFER_REQUESTED", entity_type="transfer",
                        entity_id=transfer.id, performed_by=employees[1].id,
                        description="Transfer requested: Dell XPS from Sneha to Vikram"),
            ActivityLog(action="MAINTENANCE_REQUESTED", entity_type="maintenance",
                        entity_id=maint.id, performed_by=employees[4].id,
                        description="Maintenance requested for MacBook Air"),
            ActivityLog(action="MAINTENANCE_APPROVED", entity_type="maintenance",
                        entity_id=maint.id, performed_by=employees[0].id,
                        description="Maintenance approved by admin"),
        ]
        db.add_all(activities)

        db.commit()
        print("\n🎉 Seed complete! Demo scenarios ready:")
        print("   • Overdue return: MacBook Pro (Rahul) — 5 days overdue")
        print("   • Mid-transfer:  Dell XPS (Sneha → Vikram) — pending approval")
        print("   • Under repair:  MacBook Air — battery replacement approved")
        print("   • Available:     ThinkPad X1, HP EliteBook, monitors, phones, accessories")
        print("   • Retired:       Steelcase Leap V2 chair")
        print(f"\n🔐 Login: arjun.sharma@assetflow.com / password123 (Admin)")
        print(f"🔐 Login: priya.patel@assetflow.com / password123 (Manager)")
        print(f"🔐 Login: rahul.kumar@assetflow.com / password123 (Employee)")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
