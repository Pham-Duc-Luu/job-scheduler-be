from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import JobByMachine, JobByMachineOperate
from app.schemas.JobOperater import BatchJobOpTimeUpdate
from app.schemas.job import JobCreate, JobRead, JobUpdate
from app.services.job_service import (
    create_job_in_cycle,
    delete_job_in_cycle,
    update_job_in_cycle,
    get_jobs_in_cycle,
    validate_cycle,
    validate_factory
)

router = APIRouter(
    prefix="/company/{company_id}/factory/{factory_id}/cycle/{cycle_id}/job",
    tags=["Job By Machine In Cycle"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------- CRUD Job -----------------------

@router.post("/", response_model=JobRead)
def create_job(
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_data: JobCreate,
    db: Session = Depends(get_db),
):
    return create_job_in_cycle(db, company_id, factory_id, cycle_id, job_data)


@router.put("/{job_id}", response_model=JobRead)
def update_job(
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_id: int,
    update_data: JobUpdate,
    db: Session = Depends(get_db),
):
    return update_job_in_cycle(db, company_id, factory_id, cycle_id, job_id, update_data)


@router.get("/", response_model=List[JobRead])
def list_jobs(
    company_id: int,
    factory_id: int,
    cycle_id: int,
    db: Session = Depends(get_db),
):
    return get_jobs_in_cycle(db, company_id, factory_id, cycle_id)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_id: int,
    db: Session = Depends(get_db),
):
    delete_job_in_cycle(db, company_id, factory_id, cycle_id, job_id)
    return
