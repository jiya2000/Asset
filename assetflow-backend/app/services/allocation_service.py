"""
Allocation service — orchestrates the allocate / approve / return / transfer
workflows.  This is the centerpiece demo logic.

Flow:
  1. allocate_asset    → creates PENDING allocation
  2. approve_allocation → PENDING → ACTIVE, asset → ALLOCATED
  3. return_asset       → ACTIVE → RETURNED, asset → AVAILABLE
  4. initiate_transfer  → creates PENDING transfer + new PENDING allocation
  5. approve_transfer   → completes old allocation, activates new one
"""

from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetStatus
from app.models.allocation import (
    Allocation, AllocationStatus, Transfer, TransferStatus,
)
from app.models.user import Employee
from app.repositories.allocation_repo import AllocationRepository, TransferRepository
from app.repositories.asset_repo import AssetRepository
from app.repositories.activity_repo import ActivityRepository
from app.validators.allocation_rules import (
    validate_asset_available,
    validate_no_active_allocation,
    validate_employee_active,
    validate_allocation_pending,
    validate_allocation_active,
    validate_transfer_different_employees,
    validate_asset_held_by_employee,
)


class AllocationService:

    # ── Allocate ──────────────────────────────────────────────────────────

    @staticmethod
    def allocate_asset(
        db: Session,
        asset_id: int,
        employee_id: int,
        current_user: Employee,
        expected_return: datetime = None,
        purpose: str = None,
        notes: str = None,
    ) -> Allocation:
        # fetch & validate
        asset = AssetRepository.get_by_id(db, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        validate_asset_available(asset)
        validate_no_active_allocation(db, asset_id)
        validate_employee_active(employee)

        # create pending allocation
        alloc = AllocationRepository.create(
            db,
            asset_id=asset_id,
            employee_id=employee_id,
            expected_return=expected_return,
            purpose=purpose,
            notes=notes,
            status=AllocationStatus.PENDING,
        )

        # log activity
        ActivityRepository.log(
            db,
            action="ALLOCATION_REQUESTED",
            entity_type="allocation",
            entity_id=alloc.id,
            performed_by=current_user.id,
            description=f"Allocation requested: asset {asset.asset_tag} → employee {employee.emp_code}",
        )

        return alloc

    # ── Approve ───────────────────────────────────────────────────────────

    @staticmethod
    def approve_allocation(
        db: Session,
        allocation_id: int,
        approver: Employee,
    ) -> Allocation:
        alloc = AllocationRepository.get_by_id(db, allocation_id)
        if not alloc:
            raise HTTPException(status_code=404, detail="Allocation not found")

        validate_allocation_pending(alloc)

        # also re-check asset is still available (race-condition guard)
        asset = AssetRepository.get_by_id(db, alloc.asset_id)
        validate_asset_available(asset)

        now = datetime.now(timezone.utc)
        alloc.status = AllocationStatus.ACTIVE
        alloc.approved_by = approver.id
        alloc.approved_at = now
        alloc.allocated_at = now

        # transition asset status
        asset.status = AssetStatus.ALLOCATED
        db.commit()
        db.refresh(alloc)

        ActivityRepository.log(
            db,
            action="ALLOCATION_APPROVED",
            entity_type="allocation",
            entity_id=alloc.id,
            performed_by=approver.id,
            description=f"Allocation approved by {approver.emp_code}",
        )

        return alloc

    # ── Return ────────────────────────────────────────────────────────────

    @staticmethod
    def return_asset(
        db: Session,
        allocation_id: int,
        current_user: Employee,
        notes: str = None,
    ) -> Allocation:
        alloc = AllocationRepository.get_by_id(db, allocation_id)
        if not alloc:
            raise HTTPException(status_code=404, detail="Allocation not found")

        validate_allocation_active(alloc)

        now = datetime.now(timezone.utc)
        alloc.status = AllocationStatus.RETURNED
        alloc.actual_return = now
        if notes:
            alloc.notes = (alloc.notes or "") + f"\nReturn note: {notes}"

        # asset becomes available again
        asset = AssetRepository.get_by_id(db, alloc.asset_id)
        asset.status = AssetStatus.AVAILABLE
        db.commit()
        db.refresh(alloc)

        ActivityRepository.log(
            db,
            action="ASSET_RETURNED",
            entity_type="allocation",
            entity_id=alloc.id,
            performed_by=current_user.id,
            description=f"Asset {asset.asset_tag} returned",
        )

        return alloc

    # ── Transfer ──────────────────────────────────────────────────────────

    @staticmethod
    def initiate_transfer(
        db: Session,
        asset_id: int,
        from_employee_id: int,
        to_employee_id: int,
        current_user: Employee,
        reason: str = None,
    ) -> Transfer:
        validate_transfer_different_employees(from_employee_id, to_employee_id)

        asset = AssetRepository.get_by_id(db, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # find current active allocation
        current_alloc = AllocationRepository.get_active_for_asset(db, asset_id)
        if not current_alloc:
            raise HTTPException(
                status_code=409,
                detail="Asset has no active allocation — cannot transfer.",
            )

        validate_asset_held_by_employee(current_alloc, from_employee_id)

        to_employee = db.query(Employee).filter(Employee.id == to_employee_id).first()
        if not to_employee:
            raise HTTPException(status_code=404, detail="Target employee not found")
        validate_employee_active(to_employee)

        # create transfer record
        transfer = TransferRepository.create(
            db,
            asset_id=asset_id,
            from_employee_id=from_employee_id,
            to_employee_id=to_employee_id,
            from_allocation_id=current_alloc.id,
            reason=reason,
            status=TransferStatus.PENDING,
        )

        ActivityRepository.log(
            db,
            action="TRANSFER_REQUESTED",
            entity_type="transfer",
            entity_id=transfer.id,
            performed_by=current_user.id,
            description=f"Transfer requested: asset {asset.asset_tag} from {from_employee_id} → {to_employee_id}",
        )

        return transfer

    # ── Approve Transfer ──────────────────────────────────────────────────

    @staticmethod
    def approve_transfer(
        db: Session,
        transfer_id: int,
        approver: Employee,
    ) -> Transfer:
        transfer = TransferRepository.get_by_id(db, transfer_id)
        if not transfer:
            raise HTTPException(status_code=404, detail="Transfer not found")

        if transfer.status != TransferStatus.PENDING:
            raise HTTPException(
                status_code=409,
                detail=f"Transfer is '{transfer.status.value}', not 'pending'.",
            )

        now = datetime.now(timezone.utc)

        # close old allocation
        old_alloc = AllocationRepository.get_by_id(db, transfer.from_allocation_id)
        old_alloc.status = AllocationStatus.RETURNED
        old_alloc.actual_return = now

        # create new allocation for the receiving employee
        new_alloc = AllocationRepository.create(
            db,
            asset_id=transfer.asset_id,
            employee_id=transfer.to_employee_id,
            status=AllocationStatus.ACTIVE,
            allocated_at=now,
            approved_by=approver.id,
            approved_at=now,
            purpose=f"Transfer from employee {transfer.from_employee_id}",
        )

        # update transfer
        transfer.to_allocation_id = new_alloc.id
        transfer.status = TransferStatus.COMPLETED
        transfer.approved_by = approver.id
        transfer.approved_at = now
        transfer.completed_at = now
        db.commit()
        db.refresh(transfer)

        ActivityRepository.log(
            db,
            action="TRANSFER_COMPLETED",
            entity_type="transfer",
            entity_id=transfer.id,
            performed_by=approver.id,
            description=f"Transfer approved by {approver.emp_code}",
        )

        return transfer

    # ── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def get_all_allocations(db: Session, alloc_status=None) -> List[Allocation]:
        return AllocationRepository.get_all(db, status=alloc_status)

    @staticmethod
    def get_allocation(db: Session, allocation_id: int) -> Allocation:
        alloc = AllocationRepository.get_by_id(db, allocation_id)
        if not alloc:
            raise HTTPException(status_code=404, detail="Allocation not found")
        return alloc

    @staticmethod
    def get_all_transfers(db: Session) -> List[Transfer]:
        return TransferRepository.get_all(db)

    @staticmethod
    def get_pending_approvals(db: Session) -> dict:
        """Approval center — all pending allocations and transfers."""
        return {
            "pending_allocations": AllocationRepository.get_pending(db),
            "pending_transfers": TransferRepository.get_pending(db),
        }
