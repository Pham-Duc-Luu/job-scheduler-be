from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class Task(BaseModel):
    job: int
    task_index: int
    start: int
    end: int
    duration: int


class Machine(BaseModel):
    machine_id: str
    tasks: List[Task]


class FactoryCycleBase(BaseModel):
    name: str
    description: Optional[str] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    status: Optional[str] = "draft"
    cycle_schedula: Optional[List[Machine]] = None


class FactoryCycleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    status: Optional[str] = "draft"
    pass


class FactoryCycleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    status: Optional[str] = None
    cycle_schedula: Optional[List[Machine]] = None


class FactoryCycleResponse(FactoryCycleBase):
    id: int
    factoryId: int

    class Config:
        orm_mode = True
