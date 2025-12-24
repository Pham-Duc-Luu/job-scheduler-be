from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import JobByMachine, Factory, FactoryCycle, JobByMachineOperate
from app.schemas.job import JobCreate, JobRead, JobUpdate


# -----------------------------
# Helper functions
# -----------------------------

def validate_factory(db: Session, company_id: int, factory_id: int):
    factory = db.query(Factory).filter(
        Factory.id == factory_id,
        Factory.companyId == company_id
    ).first()

    if not factory:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhà máy trong công ty."
        )
    return factory


def validate_cycle(db: Session, factory_id: int, cycle_id: int):
    cycle = db.query(FactoryCycle).filter(
        FactoryCycle.id == cycle_id,
        FactoryCycle.factoryId == factory_id
    ).first()

    if not cycle:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy FactoryCycle."
        )
    return cycle


# -----------------------------
# CREATE JOB
# -----------------------------

def create_job_in_cycle(
    db: Session,
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_data: JobCreate
) -> JobRead:

    validate_factory(db, company_id, factory_id)
    validate_cycle(db, factory_id, cycle_id)

    job = JobByMachine(
        factoryCycleId=cycle_id,
        name=job_data.name,
        description=job_data.description,
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# -----------------------------
# UPDATE JOB
# -----------------------------

def update_job_in_cycle(
    db: Session,
    company_id: int,
    factory_id: int,
    cycle_id: int,
    job_id: int,
    update_data: JobUpdate
) -> JobRead:

    validate_factory(db, company_id, factory_id)
    validate_cycle(db, factory_id, cycle_id)

    job = db.query(JobByMachine).filter(
        JobByMachine.id == job_id,
        JobByMachine.factoryCycleId == cycle_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Job trong Cycle."
        )

    # Update fields
    if update_data.name is not None:
        job.name = update_data.name

    if update_data.description is not None:
        job.description = update_data.description

    if update_data.listOperatorTask is not None:
        job.listOperatorTask = [item.dict()
                                for item in update_data.listOperatorTask]

    db.commit()
    db.refresh(job)

    return job


# -----------------------------
# LIST JOBS
# -----------------------------

def get_jobs_in_cycle(
    db: Session,
    company_id: int,
    factory_id: int,
    cycle_id: int
) -> list[JobRead]:

    validate_factory(db, company_id, factory_id)
    validate_cycle(db, factory_id, cycle_id)

    jobs = db.query(JobByMachine).options(
        joinedload(JobByMachine.job_ops)
        .joinedload(JobByMachineOperate.machine)   # 👈 JOIN machine
    ).filter(
        JobByMachine.factoryCycleId == cycle_id
    ).all()

    return jobs


def delete_job_in_cycle(db: Session, company_id: int, factory_id: int, cycle_id: int, job_id: int):
    job = (
        db.query(JobByMachine)
        .filter(
            JobByMachine.id == job_id,
            JobByMachine.factoryCycleId == cycle_id
        )
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()
