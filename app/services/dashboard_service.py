"""
Dashboard service — KPIs, smart insights, and activity feed.

Smart insights detect real operational issues:
  • Overdue asset returns
  • Warranties expiring within 30 days
  • Assets with repeated maintenance (>2 requests)
  • Departments with high allocation density
"""

from datetime import datetime, timezone, timedelta, date
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.asset import Asset, AssetStatus
from app.models.allocation import Allocation, AllocationStatus
from app.models.maintenance import MaintenanceRequest, MaintenanceStatus
from app.models.user import Employee, Department
from app.models.activity_log import ActivityLog
from app.repositories.asset_repo import AssetRepository
from app.repositories.allocation_repo import AllocationRepository
from app.repositories.activity_repo import ActivityRepository
from app.schemas.dashboard import DashboardKPIs, SmartInsight, ActivityLogResponse


class DashboardService:

    @staticmethod
    def get_kpis(db: Session) -> DashboardKPIs:
        now = datetime.now(timezone.utc)

        total_assets = db.query(func.count(Asset.id)).filter(Asset.is_active == True).scalar()
        available = db.query(func.count(Asset.id)).filter(
            Asset.is_active == True, Asset.status == AssetStatus.AVAILABLE
        ).scalar()
        allocated = db.query(func.count(Asset.id)).filter(
            Asset.is_active == True, Asset.status == AssetStatus.ALLOCATED
        ).scalar()
        under_maint = db.query(func.count(Asset.id)).filter(
            Asset.is_active == True, Asset.status == AssetStatus.UNDER_MAINTENANCE
        ).scalar()
        retired = db.query(func.count(Asset.id)).filter(
            Asset.is_active == True, Asset.status == AssetStatus.RETIRED
        ).scalar()
        total_employees = db.query(func.count(Employee.id)).filter(Employee.is_active == True).scalar()
        active_allocs = AllocationRepository.count_active(db)
        pending = AllocationRepository.count_pending(db)
        overdue = AllocationRepository.count_overdue(db)

        # pending maintenance requests count
        pending_maint = db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.status == MaintenanceStatus.PENDING
        ).scalar()

        return DashboardKPIs(
            total_assets=total_assets or 0,
            available_assets=available or 0,
            allocated_assets=allocated or 0,
            under_maintenance=under_maint or 0,
            retired_assets=retired or 0,
            total_employees=total_employees or 0,
            active_allocations=active_allocs or 0,
            pending_approvals=(pending or 0) + (pending_maint or 0),
            overdue_returns=overdue or 0,
            assets_by_category=AssetRepository.count_by_category(db),
            assets_by_department=AssetRepository.count_by_department(db),
            assets_by_status=AssetRepository.count_by_status(db),
        )

    @staticmethod
    def get_smart_insights(db: Session) -> List[SmartInsight]:
        insights = []
        now = datetime.now(timezone.utc)

        # 1. Overdue returns
        overdue_allocs = AllocationRepository.get_overdue(db)
        for alloc in overdue_allocs:
            days_overdue = (now - alloc.expected_return).days
            insights.append(SmartInsight(
                insight_type="overdue_return",
                severity="critical" if days_overdue > 7 else "warning",
                message=f"Asset (allocation #{alloc.id}) is {days_overdue} days overdue for return. "
                        f"Expected return was {alloc.expected_return.strftime('%Y-%m-%d')}.",
                related_entity_type="allocation",
                related_entity_id=alloc.id,
            ))

        # 2. Warranties expiring within 30 days
        threshold = date.today() + timedelta(days=30)
        expiring_assets = (
            db.query(Asset)
            .filter(
                Asset.is_active == True,
                Asset.warranty_expiry != None,
                Asset.warranty_expiry <= threshold,
                Asset.warranty_expiry >= date.today(),
            )
            .all()
        )
        for asset in expiring_assets:
            days_left = (asset.warranty_expiry - date.today()).days
            insights.append(SmartInsight(
                insight_type="warranty_expiring",
                severity="warning",
                message=f"Asset '{asset.asset_tag}' ({asset.name}) warranty expires in {days_left} days "
                        f"on {asset.warranty_expiry.strftime('%Y-%m-%d')}.",
                related_entity_type="asset",
                related_entity_id=asset.id,
            ))

        # 3. High-maintenance assets (more than 2 requests)
        high_maint = (
            db.query(MaintenanceRequest.asset_id, func.count(MaintenanceRequest.id).label("cnt"))
            .group_by(MaintenanceRequest.asset_id)
            .having(func.count(MaintenanceRequest.id) > 2)
            .all()
        )
        for asset_id, count in high_maint:
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if asset:
                insights.append(SmartInsight(
                    insight_type="high_maintenance",
                    severity="info",
                    message=f"Asset '{asset.asset_tag}' has had {count} maintenance requests. "
                            f"Consider retirement or replacement.",
                    related_entity_type="asset",
                    related_entity_id=asset.id,
                ))

        return insights

    @staticmethod
    def get_recent_activity(db: Session, limit: int = 20) -> List[ActivityLog]:
        return ActivityRepository.get_recent(db, limit=limit)

    @staticmethod
    def get_asset_timeline(db: Session, asset_id: int) -> List[ActivityLog]:
        return ActivityRepository.get_for_entity(db, "asset", asset_id)
