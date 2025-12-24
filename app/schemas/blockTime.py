
# Pydantic model cho response
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Pydantic model cho request body


class BlockTimeRequest(BaseModel):
    job_type: str | None = None
    job_duration: int  # đơn vị: phút hoặc giờ tùy định nghĩa
    requested_datetime: datetime
    title: str
    description: str | None = None


class BlockTimeResponse(BaseModel):
    id: int
    employee_id: int
    job_type: str | None = None
    job_duration: int
    requested_datetime: datetime
    title: str
    description: str | None

    class Config:
        orm_mode = True
# Pydantic model cho update


class BlockTimeUpdateRequest(BaseModel):
    job_type: Optional[str] = None
    job_duration: Optional[int] = None
    requested_datetime: Optional[datetime] = None
    title: Optional[str] = None
    description: Optional[str] = None
