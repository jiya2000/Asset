"""
Activity log — immutable audit trail for every meaningful action.

This is append-only; no updates or deletes.  The dashboard can query it
for "recent activity" and the asset timeline view.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id          = Column(Integer, primary_key=True, index=True)
    action      = Column(String(100), nullable=False)     # e.g. "ASSET_CREATED", "ALLOCATION_APPROVED"
    entity_type = Column(String(50), nullable=False)       # e.g. "asset", "allocation"
    entity_id   = Column(Integer, nullable=False)
    description = Column(Text)
    performed_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # relationships
    performer = relationship("Employee")

    def __repr__(self):
        return f"<ActivityLog {self.action} on {self.entity_type}#{self.entity_id}>"
