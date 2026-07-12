"""
Auth router — signup, login, profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token, get_current_user,
)
from app.models.user import Employee, Department
from app.schemas.user import (
    SignupRequest, LoginRequest, TokenResponse,
    EmployeeResponse, EmployeeUpdate,
    DepartmentCreate, DepartmentResponse, DepartmentUpdate,
)
from app.core.rbac import require_role
from app.models.user import RoleEnum
from app.repositories.activity_repo import ActivityRepository

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Signup ────────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=EmployeeResponse, status_code=201)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    # unique checks
    if db.query(Employee).filter(Employee.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if db.query(Employee).filter(Employee.emp_code == data.emp_code).first():
        raise HTTPException(status_code=409, detail="Employee code already exists")

    emp = Employee(
        emp_code=data.emp_code,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        phone=data.phone,
        department_id=data.department_id,
        role=data.role,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)

    ActivityRepository.log(
        db,
        action="EMPLOYEE_REGISTERED",
        entity_type="employee",
        entity_id=emp.id,
        performed_by=emp.id,
        description=f"New employee registered: {emp.emp_code}",
    )
    return emp


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.email == data.email).first()
    if not emp or not verify_password(data.password, emp.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not emp.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    token = create_access_token({"sub": emp.id, "role": emp.role.value})
    return TokenResponse(access_token=token, user=EmployeeResponse.model_validate(emp))


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("/me", response_model=EmployeeResponse)
def get_profile(current_user: Employee = Depends(get_current_user)):
    return current_user


# ── Employee Directory ────────────────────────────────────────────────────────

@router.get("/employees", response_model=list[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return db.query(Employee).filter(Employee.is_active == True).order_by(Employee.emp_code).all()


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.is_active == True).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.patch("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN)),
):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(emp, key, value)
    db.commit()
    db.refresh(emp)
    return emp


# ── Departments ───────────────────────────────────────────────────────────────

@router.post("/departments", response_model=DepartmentResponse, status_code=201)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN)),
):
    if db.query(Department).filter(Department.code == data.code).first():
        raise HTTPException(status_code=409, detail="Department code already exists")
    dept = Department(name=data.name, code=data.code, description=data.description)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()


@router.patch("/departments/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role(RoleEnum.ADMIN)),
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dept, key, value)
    db.commit()
    db.refresh(dept)
    return dept
