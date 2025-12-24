from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    planning = "planning"
    pending = "pending"
    finish = "finish"


class JobByEmployeeCreate(BaseModel):
    duration: int = Field(..., gt=0)
    name: str
    skillNeeded: str
    description: Optional[str] = None

    expected_weekday: int = Field(..., ge=0, le=6)
    # start_hour: int = Field(..., ge=0, le=23)
    # end_hour: int = Field(..., ge=1, le=24)

    factoryId: int


class JobByEmployeeUpdate(BaseModel):
    duration: Optional[int] = None
    name: Optional[str] = None
    skillNeeded: Optional[str] = None
    description: Optional[str] = None

    expected_weekday: Optional[int] = Field(None, ge=0, le=4)
    start_hour: Optional[int] = Field(None, ge=0, le=23)
    end_hour: Optional[int] = Field(None, ge=1, le=24)

    status: Optional[JobStatus] = None
    finishDate: Optional[datetime] = None
    factoryId: Optional[int] = None


class FactoryReadLite(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class JobByEmployeeRead(BaseModel):
    id: int
    companyId: int

    duration: Optional[int]
    name: Optional[str]
    skillNeeded: Optional[str]
    description: Optional[str]

    expected_weekday: Optional[int]
    start_hour: Optional[int]
    end_hour: Optional[int]

    status: JobStatus
    finishDate: Optional[datetime]

    factoryId: Optional[int]
    factory: Optional[FactoryReadLite]

    class Config:
        orm_mode = True
