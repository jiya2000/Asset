"""Pydantic schemas for Dashboard KPIs and activity feed."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    total_assets: int
    available_assets: int
    allocated_assets: int
    under_maintenance: int
    retired_assets: int
    total_employees: int
    active_allocations: int
    pending_approvals: int
    overdue_returns: int
    assets_by_category: List[dict]
    assets_by_department: List[dict]
    assets_by_status: List[dict]


class ActivityLogResponse(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int
    description: Optional[str]
    performed_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SmartInsight(BaseModel):
    insight_type: str       # e.g. "overdue_return", "warranty_expiring", "high_maintenance"
    severity: str           # "info", "warning", "critical"
    message: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
