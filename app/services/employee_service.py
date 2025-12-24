from sqlalchemy.orm import Session
from app import models
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
import random
import string
from fastapi import HTTPException
from ..utils import generate_email


def generate_random_password(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_letters, k=length))


def add_new_employee_in_company(db: Session, company_id: int, employee: EmployeeCreate):
    # Verify the company exists
    company = db.query(models.Company).filter(
        models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Default password if not provided
    password = employee.password or generate_random_password()
    # Default roleList if not provided
    role_list = employee.roleList or ["STAFF"]

    db_employee = models.Employee(
        companyId=company_id,
        email=generate_email(
            fullname=employee.fullName, domain=company.domain),
        password=password,
        phoneNumber=employee.phoneNumber,
        employeeSkillList=employee.employeeSkillList,
        roleList=role_list,
        fullName=employee.fullName
    )

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def get_employees_by_company(db: Session, company_id: int):
    return db.query(models.Employee).filter(models.Employee.companyId == company_id).all()


def update_employee(db: Session, employee_id: int, employee_update: EmployeeUpdate):
    db_employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    for key, value in employee_update.dict(exclude_unset=True).items():
        setattr(db_employee, key, value)

    db.commit()
    db.refresh(db_employee)
    return db_employee
