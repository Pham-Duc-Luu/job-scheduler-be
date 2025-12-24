from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeSkillSet, EmployeeUpdate
from app.schemas.employee_distance import EmployeeFactoryDistanceByEmployeeResponse
from app.services import employee_service
from app.models import EmployeeToFactoryDistance, skill_list
router = APIRouter(prefix="/employees", tags=["Employees by admin", "Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Add a new employee to a company
@router.post("/company/{company_id}", response_model=EmployeeRead)
def add_new_employee_in_company(company_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    """
    Add a new employee to a specific company.
    - Auto generates password if not provided
    - Defaults roleList to ["STAFF"]
    """
    return employee_service.add_new_employee_in_company(db, company_id, employee)


# (Optional) Get employees of a company
@router.get("/company/{company_id}", response_model=List[EmployeeRead])
def get_employees_by_company(company_id: int, db: Session = Depends(get_db)):
    employees = employee_service.get_employees_by_company(db, company_id)

    return employees


@router.put("/employees/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, employee_update: EmployeeUpdate, db: Session = Depends(get_db)):
    return employee_service.update_employee(db, employee_id, employee_update)


# 🔍 Lấy chi tiết nhân viên trong công ty
@router.get("/company/{company_id}/{employee_id}", response_model=EmployeeRead)
def get_employee_in_company(company_id: int, employee_id: int, db: Session = Depends(get_db)):
    return employee_service.get_employee_in_company(db, company_id, employee_id)


@router.get("/employee/skillset", response_model=List[EmployeeSkillSet])
def get_employees_skilllist():

    return skill_list


@router.get("/employee/rolelist", response_model=List[EmployeeSkillSet])
def get_employees_skilllist():
    skill_list = [
        {"key": "ADMIN", "label": "Người quản trị"},
        {"key": "FACTORY_MANAGER", "label": "Người quản lí nhà máy"},
        {"key": "EQUITMENT_MANAGER", "label": "Người quản lí thiết bị"},
        {"key": "STAFF", "label": "Nhân viên thông thường"},

    ]
    return skill_list


@router.get(
    "/employees/{employeeId}/factory-distances",
    response_model=list[EmployeeFactoryDistanceByEmployeeResponse],
)
def get_factory_distances_by_employee(
    companyId: int,
    employeeId: int,
    db: Session = Depends(get_db),
):
    distances = db.query(EmployeeToFactoryDistance) .filter(
        EmployeeToFactoryDistance.companyId == companyId,
        EmployeeToFactoryDistance.employeeId == employeeId,
    ) .all()

    if not distances:
        raise HTTPException(
            status_code=404,
            detail="Nhân viên này chưa có thông tin khoảng cách đến nhà máy nào",
        )

    return distances
