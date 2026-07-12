"""
Asset repository — pure SQL access, no business rules.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.asset import Asset, Category, AssetStatus
from app.schemas.asset import AssetCreate, AssetUpdate, AssetSearchParams


class AssetRepository:

    @staticmethod
    def create(db: Session, data: AssetCreate) -> Asset:
        asset = Asset(**data.model_dump())
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def get_by_id(db: Session, asset_id: int) -> Optional[Asset]:
        return (
            db.query(Asset)
            .options(joinedload(Asset.category))
            .filter(Asset.id == asset_id, Asset.is_active == True)
            .first()
        )

    @staticmethod
    def get_by_tag(db: Session, asset_tag: str) -> Optional[Asset]:
        return db.query(Asset).filter(Asset.asset_tag == asset_tag, Asset.is_active == True).first()

    @staticmethod
    def get_by_serial(db: Session, serial_number: str) -> Optional[Asset]:
        return db.query(Asset).filter(Asset.serial_number == serial_number, Asset.is_active == True).first()

    @staticmethod
    def search(db: Session, params: AssetSearchParams) -> Tuple[List[Asset], int]:
        """Search/filter assets with pagination. Returns (items, total_count)."""
        query = db.query(Asset).options(joinedload(Asset.category)).filter(Asset.is_active == True)

        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    Asset.name.ilike(search_term),
                    Asset.asset_tag.ilike(search_term),
                    Asset.serial_number.ilike(search_term),
                )
            )
        if params.status:
            query = query.filter(Asset.status == params.status)
        if params.category_id:
            query = query.filter(Asset.category_id == params.category_id)
        if params.department_id:
            query = query.filter(Asset.department_id == params.department_id)
        if params.condition:
            query = query.filter(Asset.condition == params.condition)

        total = query.count()
        offset = (params.page - 1) * params.page_size
        items = query.order_by(Asset.created_at.desc()).offset(offset).limit(params.page_size).all()
        return items, total

    @staticmethod
    def update(db: Session, asset: Asset, data: AssetUpdate) -> Asset:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(asset, key, value)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def update_status(db: Session, asset: Asset, new_status: AssetStatus) -> Asset:
        asset.status = new_status
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def soft_delete(db: Session, asset: Asset) -> Asset:
        asset.is_active = False
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def count_by_status(db: Session) -> List[dict]:
        results = (
            db.query(Asset.status, func.count(Asset.id))
            .filter(Asset.is_active == True)
            .group_by(Asset.status)
            .all()
        )
        return [{"status": r[0].value, "count": r[1]} for r in results]

    @staticmethod
    def count_by_category(db: Session) -> List[dict]:
        results = (
            db.query(Category.name, func.count(Asset.id))
            .join(Category)
            .filter(Asset.is_active == True)
            .group_by(Category.name)
            .all()
        )
        return [{"category": r[0], "count": r[1]} for r in results]

    @staticmethod
    def count_by_department(db: Session) -> List[dict]:
        from app.models.user import Department
        results = (
            db.query(Department.name, func.count(Asset.id))
            .join(Department)
            .filter(Asset.is_active == True)
            .group_by(Department.name)
            .all()
        )
        return [{"department": r[0], "count": r[1]} for r in results]


class CategoryRepository:

    @staticmethod
    def create(db: Session, name: str, code: str, description: str = None) -> Category:
        cat = Category(name=name, code=code, description=description)
        db.add(cat)
        db.commit()
        db.refresh(cat)
        return cat

    @staticmethod
    def get_all(db: Session) -> List[Category]:
        return db.query(Category).filter(Category.is_active == True).order_by(Category.name).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id, Category.is_active == True).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Category]:
        return db.query(Category).filter(Category.code == code, Category.is_active == True).first()

    @staticmethod
    def update(db: Session, category: Category, data: dict) -> Category:
        for key, value in data.items():
            if value is not None:
                setattr(category, key, value)
        db.commit()
        db.refresh(category)
        return category
