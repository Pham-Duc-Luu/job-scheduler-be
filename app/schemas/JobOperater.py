
from typing import List, Optional
from pydantic import BaseModel


class JobOperateCreate(BaseModel):
    machineId: int
    duration: float  # hour
    opIndex: Optional[int] = None


class JobOperateUpdate(BaseModel):
    duration: Optional[float] = None
    machineId: Optional[int] = None
    # opIndex: Optional[int] = None
    start: Optional[float] = None
    end: Optional[float] = None


class MachineBase(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    manual_url: Optional[str] = None
    vendor: Optional[str] = None
    note: Optional[str] = None
    code: str

    class Config:
        orm_mode = True


class JobOperateResponse(BaseModel):
    id: int
    duration: float
    machineId: int
    jobId: int
    start: float | None
    end: float | None
    task_index: int

    machine: MachineBase | None   # 👈 JOIN ở đây

    class Config:
        orm_mode = True


class JobOpTimeUpdate(BaseModel):
    jobId: int
    task_index: int
    start: float
    end: float


class BatchJobOpTimeUpdate(BaseModel):
    items: List[JobOpTimeUpdate]
