"""
Allocation business rules — pure validation, no DB writes.

Each function raises HTTPException with a precise message if the rule fails.
This is the "conflict detection" logic that makes the demo shine.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetStatus
from app.models.allocation import Allocation, AllocationStatus
from app.models.user import Employee
from app.repositories.allocation_repo import AllocationRepository


def validate_asset_available(asset: Asset) -> None:
    """An asset must be 'available' to be allocated."""
    if asset.status != AssetStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Asset '{asset.asset_tag}' is currently '{asset.status.value}' "
                   f"and cannot be allocated. Only 'available' assets can be allocated.",
        )


def validate_no_active_allocation(db: Session, asset_id: int) -> None:
    """An asset must not already have an active or approved allocation."""
    existing = AllocationRepository.get_active_for_asset(db, asset_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Asset already has an active allocation (ID: {existing.id}) "
                   f"assigned to employee ID {existing.employee_id}. "
                   f"Return or transfer the asset first.",
        )


def validate_employee_active(employee: Employee) -> None:
    """Target employee must be an active user."""
    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee '{employee.emp_code}' is deactivated and cannot receive assets.",
        )


def validate_allocation_pending(allocation: Allocation) -> None:
    """Allocation must be PENDING to be approved."""
    if allocation.status != AllocationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Allocation is '{allocation.status.value}', not 'pending'. "
                   f"Only pending allocations can be approved.",
        )


def validate_allocation_active(allocation: Allocation) -> None:
    """Allocation must be ACTIVE to be returned."""
    if allocation.status != AllocationStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Allocation is '{allocation.status.value}', not 'active'. "
                   f"Only active allocations can be returned.",
        )


def validate_transfer_different_employees(from_id: int, to_id: int) -> None:
    """Cannot transfer an asset to the same person."""
    if from_id == to_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer an asset to the same employee who currently holds it.",
        )


def validate_asset_held_by_employee(allocation: Allocation, from_employee_id: int) -> None:
    """The 'from' employee must actually hold the asset."""
    if allocation.employee_id != from_employee_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee {from_employee_id} does not currently hold this asset. "
                   f"It is held by employee {allocation.employee_id}.",
        )
