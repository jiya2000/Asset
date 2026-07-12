"""
Allocation & Transfer models.

Design decisions
────────────────
• Allocation tracks the full lifecycle: allocated → returned, with expected
  and actual return dates (enables overdue detection).
• Transfer is a separate table linking two allocations — "from_allocation" is
  being returned and "to_allocation" is being created — rather than mutating
  an existing allocation row. This preserves audit history.
• Both tables carry an `approved_by` FK for the approval workflow.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, DateTime, Enum, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class AllocationStatus(str, enum.Enum):
    PENDING   = "pending"
    APPROVED  = "approved"
    ACTIVE    = "active"
    RETURNED  = "returned"
    CANCELLED = "cancelled"


class TransferStatus(str, enum.Enum):
    PENDING   = "pending"
    APPROVED  = "approved"
    COMPLETED = "completed"
    REJECTED  = "rejected"


# ── Allocation ────────────────────────────────────────────────────────────────

class Allocation(Base):
    __tablename__ = "allocations"

    id                  = Column(Integer, primary_key=True, index=True)
    asset_id            = Column(Integer, ForeignKey("assets.id"), nullable=False)
    employee_id         = Column(Integer, ForeignKey("employees.id"), nullable=False)
    status              = Column(Enum(AllocationStatus), default=AllocationStatus.PENDING, nullable=False)
    allocated_at        = Column(DateTime(timezone=True))
    expected_return     = Column(DateTime(timezone=True))
    actual_return       = Column(DateTime(timezone=True))
    purpose             = Column(String(500))
    notes               = Column(Text)
    approved_by         = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_at         = Column(DateTime(timezone=True))
    created_at          = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at          = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                                 onupdate=lambda: datetime.now(timezone.utc))

    # relationships
    asset             = relationship("Asset", back_populates="allocations")
    employee          = relationship("Employee", back_populates="allocations", foreign_keys=[employee_id])
    approved_by_user  = relationship("Employee", back_populates="approved_allocations", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<Allocation {self.id}: asset={self.asset_id} → emp={self.employee_id} [{self.status.value}]>"


# ── Transfer ──────────────────────────────────────────────────────────────────

class Transfer(Base):
    __tablename__ = "transfers"

    id                  = Column(Integer, primary_key=True, index=True)
    asset_id            = Column(Integer, ForeignKey("assets.id"), nullable=False)
    from_employee_id    = Column(Integer, ForeignKey("employees.id"), nullable=False)
    to_employee_id      = Column(Integer, ForeignKey("employees.id"), nullable=False)
    from_allocation_id  = Column(Integer, ForeignKey("allocations.id"), nullable=False)
    to_allocation_id    = Column(Integer, ForeignKey("allocations.id"), nullable=True)
    status              = Column(Enum(TransferStatus), default=TransferStatus.PENDING, nullable=False)
    reason              = Column(String(500))
    approved_by         = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_at         = Column(DateTime(timezone=True))
    completed_at        = Column(DateTime(timezone=True))
    created_at          = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at          = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                                 onupdate=lambda: datetime.now(timezone.utc))

    # relationships
    asset           = relationship("Asset")
    from_employee   = relationship("Employee", foreign_keys=[from_employee_id])
    to_employee     = relationship("Employee", foreign_keys=[to_employee_id])
    from_allocation = relationship("Allocation", foreign_keys=[from_allocation_id])
    to_allocation   = relationship("Allocation", foreign_keys=[to_allocation_id])
    approver        = relationship("Employee", foreign_keys=[approved_by])

    def __repr__(self):
        return f"<Transfer {self.id}: {self.from_employee_id} → {self.to_employee_id} [{self.status.value}]>"
