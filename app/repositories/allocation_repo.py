"""
Allocation & Transfer repository — pure SQL access.
"""

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.allocation import Allocation, Transfer, AllocationStatus, TransferStatus
from app.models.asset import AssetStatus


class AllocationRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> Allocation:
        alloc = Allocation(**kwargs)
        db.add(alloc)
        db.commit()
        db.refresh(alloc)
        return alloc

    @staticmethod
    def get_by_id(db: Session, alloc_id: int) -> Optional[Allocation]:
        return db.query(Allocation).filter(Allocation.id == alloc_id).first()

    @staticmethod
    def get_active_for_asset(db: Session, asset_id: int) -> Optional[Allocation]:
        """Find the current active allocation for an asset."""
        return (
            db.query(Allocation)
            .filter(
                Allocation.asset_id == asset_id,
                Allocation.status.in_([AllocationStatus.ACTIVE, AllocationStatus.APPROVED]),
            )
            .first()
        )

    @staticmethod
    def get_active_for_employee(db: Session, employee_id: int) -> List[Allocation]:
        return (
            db.query(Allocation)
            .filter(
                Allocation.employee_id == employee_id,
                Allocation.status == AllocationStatus.ACTIVE,
            )
            .all()
        )

    @staticmethod
    def get_all(db: Session, status: Optional[AllocationStatus] = None) -> List[Allocation]:
        query = db.query(Allocation).order_by(Allocation.created_at.desc())
        if status:
            query = query.filter(Allocation.status == status)
        return query.all()

    @staticmethod
    def get_pending(db: Session) -> List[Allocation]:
        return (
            db.query(Allocation)
            .filter(Allocation.status == AllocationStatus.PENDING)
            .order_by(Allocation.created_at.desc())
            .all()
        )

    @staticmethod
    def count_active(db: Session) -> int:
        return db.query(func.count(Allocation.id)).filter(
            Allocation.status == AllocationStatus.ACTIVE
        ).scalar()

    @staticmethod
    def count_pending(db: Session) -> int:
        return db.query(func.count(Allocation.id)).filter(
            Allocation.status == AllocationStatus.PENDING
        ).scalar()

    @staticmethod
    def get_overdue(db: Session) -> List[Allocation]:
        now = datetime.now(timezone.utc)
        return (
            db.query(Allocation)
            .filter(
                Allocation.status == AllocationStatus.ACTIVE,
                Allocation.expected_return < now,
                Allocation.actual_return.is_(None),
            )
            .all()
        )

    @staticmethod
    def count_overdue(db: Session) -> int:
        now = datetime.now(timezone.utc)
        return db.query(func.count(Allocation.id)).filter(
            Allocation.status == AllocationStatus.ACTIVE,
            Allocation.expected_return < now,
            Allocation.actual_return.is_(None),
        ).scalar()


class TransferRepository:

    @staticmethod
    def create(db: Session, **kwargs) -> Transfer:
        transfer = Transfer(**kwargs)
        db.add(transfer)
        db.commit()
        db.refresh(transfer)
        return transfer

    @staticmethod
    def get_by_id(db: Session, transfer_id: int) -> Optional[Transfer]:
        return db.query(Transfer).filter(Transfer.id == transfer_id).first()

    @staticmethod
    def get_pending(db: Session) -> List[Transfer]:
        return (
            db.query(Transfer)
            .filter(Transfer.status == TransferStatus.PENDING)
            .order_by(Transfer.created_at.desc())
            .all()
        )

    @staticmethod
    def get_all(db: Session) -> List[Transfer]:
        return db.query(Transfer).order_by(Transfer.created_at.desc()).all()
