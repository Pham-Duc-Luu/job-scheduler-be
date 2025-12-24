from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any

from app.models import Employee


class EmployeeBase(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None
    employeeSkillList: Optional[List[str]] = None
    roleList: Optional[List[str]] = ["STAFF"]
    fullName: Optional[str] = None
    password: Optional[str] = None


class EmployeeSkillSet(BaseModel):
    key: str
    label: str


class EmployeeCreate(EmployeeBase):
    password: Optional[str] = None


class EmployeeUpdate(BaseModel):
    fullName: Optional[str] = None
    phoneNumber: Optional[str] = None
    employeeSkillList: Optional[Any] = None
    roleList: Optional[List[str]] = None
    locationId: Optional[int] = None
    password: Optional[str] = None


class EmployeeRead(EmployeeBase):
    id: int
    companyId: int

    class Config:
        orm_mode = True


def map_employee_to_read(employee: Employee) -> EmployeeRead:
    return EmployeeRead(
        id=employee.id,
        companyId=employee.companyId,
        email=employee.email,
        fullName=employee.fullName,
        phoneNumber=employee.phoneNumber,
        employeeSkillList=employee.employeeSkillList or [],
        roleList=employee.roleList or []
    )
