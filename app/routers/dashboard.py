"""
Dashboard router — KPIs, smart insights, activity feed, asset timeline.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import Employee
from app.schemas.dashboard import DashboardKPIs, SmartInsight, ActivityLogResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/kpis", response_model=DashboardKPIs)
def get_kpis(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return DashboardService.get_kpis(db)


@router.get("/insights", response_model=list[SmartInsight])
def get_insights(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return DashboardService.get_smart_insights(db)


@router.get("/activity", response_model=list[ActivityLogResponse])
def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return DashboardService.get_recent_activity(db, limit=limit)


@router.get("/timeline/{asset_id}", response_model=list[ActivityLogResponse])
def get_asset_timeline(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return DashboardService.get_asset_timeline(db, asset_id)
