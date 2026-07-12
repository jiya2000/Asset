"""
Maintenance business rules — pure validation.
"""

from fastapi import HTTPException, status

from app.models.asset import Asset, AssetStatus
from app.models.maintenance import MaintenanceRequest, MaintenanceStatus


def validate_asset_exists_and_active(asset: Asset) -> None:
    if not asset or not asset.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found or has been retired.",
        )


def validate_maintenance_pending(request: MaintenanceRequest) -> None:
    if request.status != MaintenanceStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Maintenance request is '{request.status.value}', not 'pending'. "
                   f"Only pending requests can be approved.",
        )


def validate_maintenance_approved_or_in_progress(request: MaintenanceRequest) -> None:
    if request.status not in (MaintenanceStatus.APPROVED, MaintenanceStatus.IN_PROGRESS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Maintenance request is '{request.status.value}'. "
                   f"Only approved or in-progress requests can be resolved.",
        )


def validate_not_already_under_maintenance(asset: Asset) -> None:
    if asset.status == AssetStatus.UNDER_MAINTENANCE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Asset '{asset.asset_tag}' is already under maintenance.",
        )
