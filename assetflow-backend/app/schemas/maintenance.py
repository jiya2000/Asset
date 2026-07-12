"""Pydantic schemas for Maintenance requests."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.maintenance import MaintenancePriority, MaintenanceStatus


class MaintenanceCreate(BaseModel):
    asset_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: MaintenancePriority = MaintenancePriority.MEDIUM


class MaintenanceResponse(BaseModel):
    id: int
    asset_id: int
    requested_by: int
    title: str
    description: Optional[str]
    priority: MaintenancePriority
    status: MaintenanceStatus
    resolution_notes: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MaintenanceApprove(BaseModel):
    notes: Optional[str] = None


class MaintenanceResolve(BaseModel):
    resolution_notes: str = Field(..., min_length=1)
