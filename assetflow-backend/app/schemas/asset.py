"""Pydantic schemas for Asset and Category."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.asset import AssetStatus, AssetCondition


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    code: str = Field(..., min_length=1, max_length=10)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# ── Asset ─────────────────────────────────────────────────────────────────────

class AssetCreate(BaseModel):
    asset_tag: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    serial_number: str = Field(..., min_length=1, max_length=100)
    category_id: int
    condition: AssetCondition = AssetCondition.NEW
    purchase_date: Optional[date] = None
    purchase_cost: Optional[Decimal] = None
    warranty_expiry: Optional[date] = None
    location: Optional[str] = None
    department_id: Optional[int] = None


class AssetResponse(BaseModel):
    id: int
    asset_tag: str
    name: str
    description: Optional[str]
    serial_number: str
    category_id: int
    category: Optional[CategoryResponse] = None
    status: AssetStatus
    condition: AssetCondition
    purchase_date: Optional[date]
    purchase_cost: Optional[Decimal]
    warranty_expiry: Optional[date]
    location: Optional[str]
    department_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    condition: Optional[AssetCondition] = None
    purchase_date: Optional[date] = None
    purchase_cost: Optional[Decimal] = None
    warranty_expiry: Optional[date] = None
    location: Optional[str] = None
    department_id: Optional[int] = None
    status: Optional[AssetStatus] = None
    is_active: Optional[bool] = None


class AssetSearchParams(BaseModel):
    """Query parameters for asset search/filter."""
    search: Optional[str] = None        # free-text search on name/tag/serial
    status: Optional[AssetStatus] = None
    category_id: Optional[int] = None
    department_id: Optional[int] = None
    condition: Optional[AssetCondition] = None
    page: int = 1
    page_size: int = 20
