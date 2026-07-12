"""
Maintenance request model.

Workflow: Pending → Approved → In_Progress → Resolved / Rejected
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, DateTime, Enum, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class MaintenancePriority(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class MaintenanceStatus(str, enum.Enum):
    PENDING     = "pending"
    APPROVED    = "approved"
    IN_PROGRESS = "in_progress"
    RESOLVED    = "resolved"
    REJECTED    = "rejected"


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id              = Column(Integer, primary_key=True, index=True)
    asset_id        = Column(Integer, ForeignKey("assets.id"), nullable=False)
    requested_by    = Column(Integer, ForeignKey("employees.id"), nullable=False)
    title           = Column(String(200), nullable=False)
    description     = Column(Text)
    priority        = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIUM, nullable=False)
    status          = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING, nullable=False)
    resolution_notes = Column(Text)
    approved_by     = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_at     = Column(DateTime(timezone=True))
    resolved_at     = Column(DateTime(timezone=True))
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc))

    # relationships
    asset        = relationship("Asset", back_populates="maintenance_requests")
    requester    = relationship("Employee", foreign_keys=[requested_by])
    approver     = relationship("Employee", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<Maintenance {self.id}: asset={self.asset_id} [{self.status.value}]>"
