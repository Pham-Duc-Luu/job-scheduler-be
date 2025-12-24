# schemas/job.py
from pydantic import BaseModel
from typing import List, Optional


class OperatorTask(BaseModel):
    machineId: int
    opDuration: float  # hour


class JobBase(BaseModel):
    name: str
    description: Optional[str] = None


class JobCreate(JobBase):
    factoryCycleId: int


class JobOperateResponse(BaseModel):
    id: int
    duration: float
    machineId: int
    start: float | None
    end: float | None
    task_index: int
    machineCode: str

    class Config:
        orm_mode = True


class JobRead(JobBase):
    id: int
    factoryCycleId: int
    job_ops: List[JobOperateResponse] = []   # 👈 thêm dòng này

    class Config:
        orm_mode = True


class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    listOperatorTask: Optional[List[OperatorTask]] = None
