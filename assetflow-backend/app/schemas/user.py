"""Pydantic schemas for authentication and user management."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import RoleEnum


# ── Auth ──────────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    emp_code: str = Field(..., min_length=1, max_length=20, examples=["EMP-001"])
    first_name: str = Field(..., min_length=1, max_length=60)
    last_name: str = Field(..., min_length=1, max_length=60)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    department_id: Optional[int] = None
    role: RoleEnum = RoleEnum.EMPLOYEE


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "EmployeeResponse"


# ── Employee ──────────────────────────────────────────────────────────────────

class EmployeeResponse(BaseModel):
    id: int
    emp_code: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    role: RoleEnum
    department_id: Optional[int]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


# ── Department ────────────────────────────────────────────────────────────────

class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    code: str = Field(..., min_length=1, max_length=10)
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# forward ref resolution
TokenResponse.model_rebuild()
