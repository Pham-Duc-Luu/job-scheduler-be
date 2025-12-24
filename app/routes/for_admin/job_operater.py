from fastapi import Body
from sqlalchemy import update
from sqlalchemy.orm import joinedload
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import SessionLocal
from sqlalchemy.orm import Session

from app.models import JobByMachine, JobByMachineOperate
from app.schemas.JobOperater import BatchJobOpTimeUpdate, JobOperateCreate, JobOperateResponse, JobOperateUpdate
from app.services.job_service import validate_cycle, validate_factory


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(
    prefix="/company/{company_id}/factory/{factory_id}/cycle/{cycle_id}/job/{job_id}",
    tags=["Job operater By Machine In Cycle"]
)


@router.post("/")
def create_job(
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_id: int,
    data: JobOperateCreate,
    db: Session = Depends(get_db),
):
    # neu la none
    if data.opIndex is None:
        count = db.query(JobByMachineOperate).filter(
            JobByMachineOperate.jobId == job_id
        ).count()

        data.opIndex = count

    jobOperater = JobByMachineOperate(
        duration=data.duration,
        machineId=data.machineId,
        jobId=job_id,
        task_index=data.opIndex
    )

    db.add(jobOperater)
    db.commit()
    db.refresh(jobOperater)
    return jobOperater


@router.post("/swap/{job_op_id_1}/{job_op_id_2}")
def swap_job_op(
    job_id: int,
    job_op_id_1: int,
    job_op_id_2: int,
    db: Session = Depends(get_db),
):

    if job_op_id_1 == job_op_id_2:
        raise HTTPException(status_code=400, detail="Không được đổi chỗ")

    op_1 = db.query(JobByMachineOperate).filter(
        JobByMachineOperate.id == job_op_id_1,
        JobByMachineOperate.jobId == job_id
    ).one_or_none()

    op_2 = db.query(JobByMachineOperate).filter(
        JobByMachineOperate.id == job_op_id_2,
        JobByMachineOperate.jobId == job_id
    ).one_or_none()

    if op_1 is None or op_2 is None:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy công việc thực hiện")

    # swap task_index
    op_1.task_index, op_2.task_index = op_2.task_index, op_1.task_index

    db.commit()

    return {"detail": "Swap successful"}


@router.get("/search", response_model=List[JobOperateResponse])
def search_job_ops(
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_id: int,
    machine_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(JobByMachineOperate).filter(
        JobByMachineOperate.jobId == job_id,
    )

    if machine_id is not None:
        query = query.filter(JobByMachineOperate.machineId == machine_id)

    return query.order_by(
        JobByMachineOperate.task_index.asc()
    ).offset(skip).limit(limit).all()


@router.put("/{job_op_id}")
def update_job_op(
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_id: int,
    job_op_id: int,
    data: JobOperateUpdate,
    db: Session = Depends(get_db),
):
    job_op = db.query(JobByMachineOperate).filter(
        JobByMachineOperate.id == job_op_id,
        JobByMachineOperate.jobId == job_id
    ).one_or_none()

    if job_op is None:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy job operation")

    # update từng field nếu có
    if data.duration is not None:
        job_op.duration = data.duration

    if data.machineId is not None:
        job_op.machineId = data.machineId

    # if data.opIndex is not None:
    #     job_op.task_index = data.opIndex

    if data.start is not None:
        job_op.start = data.start

    if data.end is not None:
        job_op.end = data.end

    db.commit()
    db.refresh(job_op)

    return job_op


@router.delete("/{job_op_id}")
def delete_job_op(
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_id: int,
    job_op_id: int,
    db: Session = Depends(get_db),
):
    job_op = db.query(JobByMachineOperate).filter(
        JobByMachineOperate.id == job_op_id,
        JobByMachineOperate.jobId == job_id
    ).one_or_none()

    if job_op is None:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy job operation")

    deleted_index = job_op.task_index

    # Xoá row
    db.delete(job_op)

    # Shift các task_index phía sau
    db.query(JobByMachineOperate).filter(
        JobByMachineOperate.jobId == job_id,
        JobByMachineOperate.task_index > deleted_index
    ).update(
        {JobByMachineOperate.task_index: JobByMachineOperate.task_index - 1},
        synchronize_session=False
    )

    db.commit()

    return {"detail": "Delete & reorder successful"}
