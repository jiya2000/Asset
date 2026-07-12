"""
Maintenance router.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.core.rbac import require_role
from app.models.user import Employee, RoleEnum
from app.models.maintenance import MaintenanceStatus
from app.schemas.maintenance import (
    MaintenanceCreate, MaintenanceResponse, MaintenanceApprove, MaintenanceResolve,
)
from app.services.maintenance_service import MaintenanceService

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


@router.post("/", response_model=MaintenanceResponse, status_code=201)
def create_request(
    data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return MaintenanceService.create_request(
        db,
        asset_id=data.asset_id,
        current_user=current_user,
        title=data.title,
        description=data.description,
        priority=data.priority,
    )


@router.get("/", response_model=list[MaintenanceResponse])
def list_requests(
    status: Optional[MaintenanceStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return MaintenanceService.get_all(db, asset_status=status)


@router.get("/pending", response_model=list[MaintenanceResponse])
def pending_requests(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    return MaintenanceService.get_pending(db)


@router.get("/{request_id}", response_model=MaintenanceResponse)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return MaintenanceService.get_by_id(db, request_id)


@router.post("/{request_id}/approve", response_model=MaintenanceResponse)
def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    return MaintenanceService.approve_request(db, request_id, approver=current_user)


@router.post("/{request_id}/start", response_model=MaintenanceResponse)
def start_maintenance(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    return MaintenanceService.start_maintenance(db, request_id, current_user)


@router.post("/{request_id}/resolve", response_model=MaintenanceResponse)
def resolve_request(
    request_id: int,
    data: MaintenanceResolve,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    return MaintenanceService.resolve_request(
        db, request_id, current_user, resolution_notes=data.resolution_notes,
    )
