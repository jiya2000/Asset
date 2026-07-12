"""
Allocations & Transfers router — thin layer over AllocationService.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.core.rbac import require_role
from app.models.user import Employee, RoleEnum
from app.models.allocation import AllocationStatus
from app.schemas.allocation import (
    AllocationCreate, AllocationResponse, AllocationApprove, AllocationReturn,
    TransferCreate, TransferResponse, TransferApprove,
)
from app.services.allocation_service import AllocationService

router = APIRouter(prefix="/api/allocations", tags=["Allocations"])


# ── Allocations ───────────────────────────────────────────────────────────────

@router.post("/", response_model=AllocationResponse, status_code=201)
def create_allocation(
    data: AllocationCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    return AllocationService.allocate_asset(
        db,
        asset_id=data.asset_id,
        employee_id=data.employee_id,
        current_user=current_user,
        expected_return=data.expected_return,
        purpose=data.purpose,
        notes=data.notes,
    )


@router.get("/", response_model=list[AllocationResponse])
def list_allocations(
    status: Optional[AllocationStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return AllocationService.get_all_allocations(db, alloc_status=status)


@router.get("/pending", response_model=dict)
def pending_approvals(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    result = AllocationService.get_pending_approvals(db)
    return {
        "pending_allocations": [AllocationResponse.model_validate(a) for a in result["pending_allocations"]],
        "pending_transfers": [TransferResponse.model_validate(t) for t in result["pending_transfers"]],
    }


@router.get("/{allocation_id}", response_model=AllocationResponse)
def get_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return AllocationService.get_allocation(db, allocation_id)


@router.post("/{allocation_id}/approve", response_model=AllocationResponse)
def approve_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    return AllocationService.approve_allocation(db, allocation_id, approver=current_user)


@router.post("/{allocation_id}/return", response_model=AllocationResponse)
def return_asset(
    allocation_id: int,
    data: AllocationReturn = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return AllocationService.return_asset(
        db, allocation_id, current_user,
        notes=data.notes if data else None,
    )


# ── Transfers ─────────────────────────────────────────────────────────────────

@router.post("/transfers", response_model=TransferResponse, status_code=201)
def create_transfer(
    data: TransferCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    return AllocationService.initiate_transfer(
        db,
        asset_id=data.asset_id,
        from_employee_id=data.from_employee_id,
        to_employee_id=data.to_employee_id,
        current_user=current_user,
        reason=data.reason,
    )


@router.get("/transfers/all", response_model=list[TransferResponse])
def list_transfers(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return AllocationService.get_all_transfers(db)


@router.post("/transfers/{transfer_id}/approve", response_model=TransferResponse)
def approve_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    return AllocationService.approve_transfer(db, transfer_id, approver=current_user)
