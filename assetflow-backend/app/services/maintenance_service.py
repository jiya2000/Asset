"""
Maintenance service — orchestrates the maintenance workflow.

Flow:  Pending → Approved → In_Progress → Resolved  (or Rejected)
When approved, asset status → UNDER_MAINTENANCE.
When resolved, asset status → AVAILABLE (or previous status).
"""

from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetStatus
from app.models.maintenance import MaintenanceRequest, MaintenanceStatus
from app.models.user import Employee
from app.repositories.asset_repo import AssetRepository
from app.repositories.activity_repo import ActivityRepository
from app.validators.maintenance_rules import (
    validate_asset_exists_and_active,
    validate_maintenance_pending,
    validate_maintenance_approved_or_in_progress,
    validate_not_already_under_maintenance,
)


class MaintenanceService:

    @staticmethod
    def create_request(
        db: Session,
        asset_id: int,
        current_user: Employee,
        title: str,
        description: str = None,
        priority: str = "medium",
    ) -> MaintenanceRequest:
        asset = AssetRepository.get_by_id(db, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        validate_asset_exists_and_active(asset)

        req = MaintenanceRequest(
            asset_id=asset_id,
            requested_by=current_user.id,
            title=title,
            description=description,
            priority=priority,
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        ActivityRepository.log(
            db,
            action="MAINTENANCE_REQUESTED",
            entity_type="maintenance",
            entity_id=req.id,
            performed_by=current_user.id,
            description=f"Maintenance requested for {asset.asset_tag}: {title}",
        )
        return req

    @staticmethod
    def approve_request(
        db: Session,
        request_id: int,
        approver: Employee,
    ) -> MaintenanceRequest:
        req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Maintenance request not found")

        validate_maintenance_pending(req)

        asset = AssetRepository.get_by_id(db, req.asset_id)
        validate_not_already_under_maintenance(asset)

        now = datetime.now(timezone.utc)
        req.status = MaintenanceStatus.APPROVED
        req.approved_by = approver.id
        req.approved_at = now

        # transition asset to under_maintenance
        asset.status = AssetStatus.UNDER_MAINTENANCE
        db.commit()
        db.refresh(req)

        ActivityRepository.log(
            db,
            action="MAINTENANCE_APPROVED",
            entity_type="maintenance",
            entity_id=req.id,
            performed_by=approver.id,
            description=f"Maintenance approved by {approver.emp_code}",
        )
        return req

    @staticmethod
    def start_maintenance(
        db: Session,
        request_id: int,
        current_user: Employee,
    ) -> MaintenanceRequest:
        req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Maintenance request not found")

        if req.status != MaintenanceStatus.APPROVED:
            raise HTTPException(status_code=409, detail="Request must be approved first.")

        req.status = MaintenanceStatus.IN_PROGRESS
        db.commit()
        db.refresh(req)

        ActivityRepository.log(
            db,
            action="MAINTENANCE_STARTED",
            entity_type="maintenance",
            entity_id=req.id,
            performed_by=current_user.id,
            description="Maintenance work started",
        )
        return req

    @staticmethod
    def resolve_request(
        db: Session,
        request_id: int,
        current_user: Employee,
        resolution_notes: str,
    ) -> MaintenanceRequest:
        req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Maintenance request not found")

        validate_maintenance_approved_or_in_progress(req)

        now = datetime.now(timezone.utc)
        req.status = MaintenanceStatus.RESOLVED
        req.resolution_notes = resolution_notes
        req.resolved_at = now

        # asset goes back to available
        asset = AssetRepository.get_by_id(db, req.asset_id)
        asset.status = AssetStatus.AVAILABLE
        db.commit()
        db.refresh(req)

        ActivityRepository.log(
            db,
            action="MAINTENANCE_RESOLVED",
            entity_type="maintenance",
            entity_id=req.id,
            performed_by=current_user.id,
            description=f"Maintenance resolved: {resolution_notes[:100]}",
        )
        return req

    @staticmethod
    def get_all(db: Session, asset_status=None) -> List[MaintenanceRequest]:
        query = db.query(MaintenanceRequest).order_by(MaintenanceRequest.created_at.desc())
        if asset_status:
            query = query.filter(MaintenanceRequest.status == asset_status)
        return query.all()

    @staticmethod
    def get_by_id(db: Session, request_id: int) -> MaintenanceRequest:
        req = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Maintenance request not found")
        return req

    @staticmethod
    def get_pending(db: Session) -> List[MaintenanceRequest]:
        return (
            db.query(MaintenanceRequest)
            .filter(MaintenanceRequest.status == MaintenanceStatus.PENDING)
            .order_by(MaintenanceRequest.created_at.desc())
            .all()
        )
