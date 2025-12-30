from typing import List
from fastapi import APIRouter, FastAPI, HTTPException, Path, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db  # SessionLocal và engine
from app.models import Employee, EmployeeBlockTime
from app.schemas.blockTime import BlockTimeRequest, BlockTimeResponse, BlockTimeUpdateRequest

router = APIRouter(prefix="/employee", tags=["Employee"])


@router.post("/{employee_id}/block-time/request")
def request_block_time(
    employee_id: int = Path(..., description="ID của nhân viên"),
    block_time: BlockTimeRequest = None,
    db: Session = Depends(get_db)
):
    # Kiểm tra employee tồn tại
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy nhân viên")

    # Tạo EmployeeBlockTime mới
    new_block_time = EmployeeBlockTime(
        employee_id=employee_id,
        job_duration=block_time.job_duration,
        # expected_weekday=block_time.requested_datetime,
        expected_weekday=block_time.expected_weekday,
        start_hour=block_time.start_hour,
        title=block_time.title,
        description=block_time.description
    )
    db.add(new_block_time)
    db.commit()
    db.refresh(new_block_time)

    return {"message": "Block time requested successfully", }


@router.get("/{employee_id}/block-time", response_model=List[BlockTimeResponse])
def get_employee_block_times(
    employee_id: int = Path(..., description="ID của nhân viên"),
    db: Session = Depends(get_db)
):
    # Kiểm tra employee tồn tại
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Lấy danh sách block time
    block_times = db.query(EmployeeBlockTime).filter(
        EmployeeBlockTime.employee_id == employee_id).all()

    return block_times


@router.put("/{employee_id}/block-time/{block_time_id}")
def update_block_time(
    employee_id: int = Path(..., description="ID của nhân viên"),
    block_time_id: int = Path(...,
                              description="ID của block time cần cập nhật"),
    block_time_update: BlockTimeUpdateRequest = None,
    db: Session = Depends(get_db)
):
    # Kiểm tra employee tồn tại
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Kiểm tra block time tồn tại
    block_time = db.query(EmployeeBlockTime).filter(
        EmployeeBlockTime.id == block_time_id,
        EmployeeBlockTime.employee_id == employee_id
    ).first()
    if not block_time:
        raise HTTPException(status_code=404, detail="Block time not found")

    # Cập nhật các field nếu được cung cấp
    for field, value in block_time_update.dict(exclude_unset=True).items():
        setattr(block_time, field, value)

    db.commit()
    db.refresh(block_time)

    return {
        "message": "Block time updated successfully",

    }
