"""
Assets router — CRUD + search/filter.
Thin layer: delegates to AssetRepository, logs to ActivityRepository.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.core.rbac import require_role
from app.models.user import Employee, RoleEnum
from app.models.asset import AssetStatus, AssetCondition
from app.schemas.asset import (
    AssetCreate, AssetResponse, AssetUpdate,
    AssetSearchParams, CategoryCreate, CategoryResponse, CategoryUpdate,
)
from app.repositories.asset_repo import AssetRepository, CategoryRepository
from app.repositories.activity_repo import ActivityRepository

router = APIRouter(prefix="/api/assets", tags=["Assets"])


# ── Categories ────────────────────────────────────────────────────────────────

@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    if CategoryRepository.get_by_code(db, data.code):
        raise HTTPException(status_code=409, detail="Category code already exists")
    return CategoryRepository.create(db, name=data.name, code=data.code, description=data.description)


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return CategoryRepository.get_all(db)


# ── Assets ────────────────────────────────────────────────────────────────────

@router.post("/", response_model=AssetResponse, status_code=201)
def register_asset(
    data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    # uniqueness checks
    if AssetRepository.get_by_tag(db, data.asset_tag):
        raise HTTPException(status_code=409, detail="Asset tag already exists")
    if AssetRepository.get_by_serial(db, data.serial_number):
        raise HTTPException(status_code=409, detail="Serial number already exists")

    # verify category exists
    if not CategoryRepository.get_by_id(db, data.category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    asset = AssetRepository.create(db, data)

    ActivityRepository.log(
        db,
        action="ASSET_REGISTERED",
        entity_type="asset",
        entity_id=asset.id,
        performed_by=current_user.id,
        description=f"Asset registered: {asset.asset_tag} ({asset.name})",
    )
    return asset


@router.get("/", response_model=dict)
def search_assets(
    search: Optional[str] = Query(None),
    status: Optional[AssetStatus] = Query(None),
    category_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    condition: Optional[AssetCondition] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    params = AssetSearchParams(
        search=search, status=status, category_id=category_id,
        department_id=department_id, condition=condition,
        page=page, page_size=page_size,
    )
    items, total = AssetRepository.search(db, params)
    return {
        "items": [AssetResponse.model_validate(a) for a in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    asset = AssetRepository.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN, RoleEnum.MANAGER)),
):
    asset = AssetRepository.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    updated = AssetRepository.update(db, asset, data)

    ActivityRepository.log(
        db,
        action="ASSET_UPDATED",
        entity_type="asset",
        entity_id=asset.id,
        performed_by=current_user.id,
        description=f"Asset updated: {asset.asset_tag}",
    )
    return updated


@router.delete("/{asset_id}", status_code=204)
def soft_delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN)),
):
    asset = AssetRepository.get_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    AssetRepository.soft_delete(db, asset)

    ActivityRepository.log(
        db,
        action="ASSET_DELETED",
        entity_type="asset",
        entity_id=asset.id,
        performed_by=current_user.id,
        description=f"Asset soft-deleted: {asset.asset_tag}",
    )
