from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from app.models import RequestStatus

# shared.py
from pydantic import BaseModel
from typing import Optional


class FactoryForMachine(BaseModel):
    name: str
    description: Optional[str] = None
    id: int
    # locationId: Optional[int] = None
    # factoryManager: Optional[int] = None

# Base model cho MachineInFactory khi trả về API


class MachineInFactoryResponse(BaseModel):
    # factoryId: int
    status: RequestStatus
    managerComment: Optional[str] = None
    factory: Optional[FactoryForMachine] = None

    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True  # rất quan trọng để Pydantic hiểu SQLAlchemy object


class MachineBase(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    manual_url: Optional[str] = None
    vendor: Optional[str] = None
    note: Optional[str] = None
    factories: Optional[List[MachineInFactoryResponse]] = Field(
        default=None, alias="machine_in_factories")

    class Config:
        orm_mode = True
        populate_by_name = True


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class MachineRead(MachineBase):
    id: int
    companyId: int
    code: str
    status: Optional[RequestStatus] = None

    class Config:
        orm_mode = True
