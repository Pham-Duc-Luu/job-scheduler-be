# schemas/employee_factory_distance.py
from pydantic import BaseModel
from typing import Optional


class EmployeeFactoryDistanceBase(BaseModel):
    factoryId: int
    employeeId: int
    distance_km: Optional[int] = None
    travel_time_hours: Optional[int] = None


class EmployeeFactoryDistanceCreate(EmployeeFactoryDistanceBase):
    pass


class EmployeeFactoryDistanceUpdate(BaseModel):
    distance_km: Optional[int] = None
    travel_time_hours: Optional[int] = None


class EmployeeFactoryDistanceResponse(EmployeeFactoryDistanceBase):
    id: int
    companyId: int

    class Config:
        from_attributes = True


# schemas/employee_factory_distance.py

class EmployeeFactoryDistanceByEmployeeResponse(BaseModel):
    id: int
    factoryId: int
    employeeId: int
    distance_km: int | None
    travel_time_hours: int | None

    class Config:
        from_attributes = True


class EmployeeFactoryDistanceUpsert(BaseModel):
    factoryId: int
    employeeId: int
    distance_km: int | None = None
    travel_time_hours: int | None = None
