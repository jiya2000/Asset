"""
Activity log repository — append-only writes, read for dashboard/timeline.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


class ActivityRepository:

    @staticmethod
    def log(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: int,
        performed_by: int,
        description: str = None,
    ) -> ActivityLog:
        entry = ActivityLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            performed_by=performed_by,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_recent(db: Session, limit: int = 20) -> List[ActivityLog]:
        return (
            db.query(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_for_entity(
        db: Session, entity_type: str, entity_id: int
    ) -> List[ActivityLog]:
        """Asset timeline — all activity for a specific entity."""
        return (
            db.query(ActivityLog)
            .filter(
                ActivityLog.entity_type == entity_type,
                ActivityLog.entity_id == entity_id,
            )
            .order_by(ActivityLog.created_at.desc())
            .all()
        )

    @staticmethod
    def get_by_user(db: Session, user_id: int, limit: int = 20) -> List[ActivityLog]:
        return (
            db.query(ActivityLog)
            .filter(ActivityLog.performed_by == user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
