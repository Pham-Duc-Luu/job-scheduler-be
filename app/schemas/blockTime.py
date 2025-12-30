
# Pydantic model cho response
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Pydantic model cho request body


class BlockTimeRequest(BaseModel):
    job_type: str | None = None
    job_duration: int  # đơn vị: phút hoặc giờ tùy định nghĩa
    # requested_datetime: datetime
    title: str
    description: str | None = None
    expected_weekday: int = Field(ge=0, le=4)
    start_hour: int = Field(ge=0, le=23)


class BlockTimeResponse(BaseModel):
    id: int
    employee_id: int
    job_type: str | None = None
    job_duration: int
    # requested_datetime: datetime
    expected_weekday: Optional[int] = Field(None, ge=0, le=4)
    title: str
    description: str | None
    start_hour: Optional[int] = Field(None, ge=0, le=23)

    class Config:
        orm_mode = True
# Pydantic model cho update


class BlockTimeUpdateRequest(BaseModel):
    job_duration: Optional[int] = None
    expected_weekday: Optional[int] = Field(None, ge=0, le=4)
    title: Optional[str] = None
    description: Optional[str] = None
    start_hour: Optional[int] = Field(None, ge=0, le=23)
