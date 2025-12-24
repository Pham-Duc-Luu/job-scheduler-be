from pydantic import BaseModel
from typing import Optional, List, Any

from app.schemas.employee import EmployeeRead
from app.schemas.machine import MachineBase, MachineRead


class machineIdINnFactory(BaseModel):
    machineId: int
    isActive: bool


class FactoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    locationId: Optional[int] = None
    factoryManager: Optional[int] = None
    machineIdList: Optional[List[machineIdINnFactory]] = None

    class Config:
        orm_mode = True  # rất quan trọng để Pydantic hiểu SQLAlchemy object


class FactoryCreate(FactoryBase):
    pass


class FactoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    locationId: Optional[int] = None
    factoryManager: Optional[int] = None
    machineIdList: Optional[List[machineIdINnFactory]] = None


class MachineInFactoryResponse(BaseModel):
    id: int
    status: str
    managerComment: str | None
    machine: MachineBase

    class Config:
        orm_mode = True


class FactoryRead(FactoryBase):
    id: int
    companyId: int
    manager: Optional[EmployeeRead] = None
    machines_in_factory: Optional[List[MachineInFactoryResponse]] = None
    machines: Optional[List[MachineRead]] = None

    class Config:
        orm_mode = True


class MachineRequestInFactory(BaseModel):
    factoryId: int
    machineId: int
