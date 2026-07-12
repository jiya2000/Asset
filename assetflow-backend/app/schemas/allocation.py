"""Pydantic schemas for Allocation and Transfer."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.allocation import AllocationStatus, TransferStatus


# ── Allocation ────────────────────────────────────────────────────────────────

class AllocationCreate(BaseModel):
    asset_id: int
    employee_id: int
    expected_return: Optional[datetime] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None


class AllocationResponse(BaseModel):
    id: int
    asset_id: int
    employee_id: int
    status: AllocationStatus
    allocated_at: Optional[datetime]
    expected_return: Optional[datetime]
    actual_return: Optional[datetime]
    purpose: Optional[str]
    notes: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AllocationApprove(BaseModel):
    notes: Optional[str] = None


class AllocationReturn(BaseModel):
    notes: Optional[str] = None


# ── Transfer ──────────────────────────────────────────────────────────────────

class TransferCreate(BaseModel):
    asset_id: int
    from_employee_id: int
    to_employee_id: int
    reason: Optional[str] = None


class TransferResponse(BaseModel):
    id: int
    asset_id: int
    from_employee_id: int
    to_employee_id: int
    from_allocation_id: int
    to_allocation_id: Optional[int]
    status: TransferStatus
    reason: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransferApprove(BaseModel):
    notes: Optional[str] = None
