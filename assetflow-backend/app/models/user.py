"""
User domain models — Employee, Department, Role.

Design decisions
────────────────
• Role is a simple enum stored on the employee row (not a join table) because
  the spec calls for a fixed set: Admin, Manager, Employee.
• Department is a first-class table so we can FK-reference it from assets &
  allocations, enabling per-department dashboards.
• Soft-delete via `is_active` flag — never physically remove a user row so
  that audit trails and FK references stay intact.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


# ── Department ────────────────────────────────────────────────────────────────

class Department(Base):
    __tablename__ = "departments"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(120), unique=True, nullable=False)
    code        = Column(String(10), unique=True, nullable=False)   # e.g. "ENG", "HR"
    description = Column(String(500))
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # relationships
    employees = relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department {self.code}>"


# ── Employee ──────────────────────────────────────────────────────────────────

class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        Index("ix_employees_email", "email", unique=True),
        Index("ix_employees_emp_code", "emp_code", unique=True),
    )

    id            = Column(Integer, primary_key=True, index=True)
    emp_code      = Column(String(20), unique=True, nullable=False)      # e.g. "EMP-001"
    first_name    = Column(String(60), nullable=False)
    last_name     = Column(String(60), nullable=False)
    email         = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    phone         = Column(String(20))
    role          = Column(Enum(RoleEnum), default=RoleEnum.EMPLOYEE, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active     = Column(Boolean, default=True, nullable=False)        # soft-delete
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # relationships
    department   = relationship("Department", back_populates="employees")
    allocations  = relationship("Allocation", back_populates="employee", foreign_keys="Allocation.employee_id")
    approved_allocations = relationship(
        "Allocation", back_populates="approved_by_user",
        foreign_keys="Allocation.approved_by",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee {self.emp_code} – {self.full_name}>"
