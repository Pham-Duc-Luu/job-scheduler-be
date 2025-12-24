from fastapi.encoders import jsonable_encoder
import datetime
from itertools import combinations
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import Company, Employee, EmployeeBlockTime, EmployeeToFactoryDistance, Factory, FactoryDistance, JobByEmployee, skill_list
from app.scheduling_optimization_ortools.main import Employee_Scheduling_Problems
from app.schemas.jobByEmployee import JobByEmployeeCreate, JobByEmployeeRead, JobByEmployeeUpdate
from sqlalchemy.exc import IntegrityError

from app.services.job_for_employee import validate_company, validate_job
from app.utils import weekday_to_date_this_week


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE


@router.post("/{company_id}", response_model=JobByEmployeeRead)
def create_job(
    company_id: int,
    job: JobByEmployeeCreate,
    db: Session = Depends(get_db)
):
    # validate_company(db, company_id)

    factory = db.query(Factory).filter(
        Factory.id == job.factoryId, Factory.companyId == company_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Địa điểm không tồn tại")

    if job.skillNeeded not in {s["key"] for s in skill_list}:
        raise HTTPException(status_code=400, detail="Kỹ năng không hợp lệ")

    db_job = JobByEmployee(
        companyId=company_id,
        name=job.name,
        skillNeeded=job.skillNeeded,
        duration=job.duration,
        description=job.description,

        expected_weekday=job.expected_weekday,
        # start_hour=job.start_hour,
        # end_hour=job.end_hour,

        factoryId=job.factoryId,
        status="planning"
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return db_job

# READ ALL


@router.get("/{company_id}",
            response_model=List[JobByEmployeeRead]
            )
def read_jobs_by_company(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Kiểm tra công ty có tồn tại hay không
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Công ty không tồn tại")

    jobs = (
        db.query(JobByEmployee)
        .options(
            joinedload(JobByEmployee.factory)
            .load_only(Factory.id, Factory.name, Factory.description),
        )
        .filter(JobByEmployee.companyId == company_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return jobs


# READ ONE

@router.get(
    "/companies/{company_id}/jobs/{job_id}",
    response_model=JobByEmployeeRead
)
def read_job(
    company_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Công ty với ID {company_id} không tồn tại."
        )

    job = (
        db.query(JobByEmployee)
        .filter(JobByEmployee.id == job_id,
                JobByEmployee.companyId == company_id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Công việc ID {job_id} không thuộc công ty {company.name}."
        )

    return job


@router.put("/{company_id}/jobs/{job_id}", response_model=JobByEmployeeRead)
def update_job(
    company_id: int,
    job_id: int,
    job_update: JobByEmployeeUpdate,
    db: Session = Depends(get_db)
):
    validate_company(db=db, company_id=company_id)
    job = validate_job(db=db, company_id=company_id, job_id=job_id)

    updates = job_update.dict(exclude_unset=True)

    # if "start_hour" in updates or "end_hour" in updates:
    #     start = updates.get("start_hour", job.start_hour)
    #     end = updates.get("end_hour", job.end_hour)
    #     if start >= end:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="start_hour phải nhỏ hơn end_hour"
    #         )

    for key, value in updates.items():
        setattr(job, key, value)

    # Auto set finishDate khi status = finish
    if updates.get("status") == "finish" and not job.finishDate:
        job.finishDate = datetime.utcnow()

    db.commit()
    db.refresh(job)
    return job


@router.delete("/companies/{company_id}/jobs/{job_id}")
def delete_job(
    company_id: int,
    job_id: int,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Công ty với ID {company_id} không tồn tại."
        )

    job = (
        db.query(JobByEmployee)
        .filter(JobByEmployee.id == job_id,
                JobByEmployee.companyId == company_id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Công việc ID {job_id} không thuộc công ty {company.name}."
        )

    db.delete(job)
    db.commit()
    return {"detail": f"Đã xóa công việc ID {job_id} của công ty {company.name} thành công."}


@router.get("/companies/{company_id}/job-json")
def getJobGeneral(
    company_id: int,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Công ty với ID {company_id} không tồn tại."
        )

    employeesQuery = db.query(Employee).filter(
        Employee.companyId == company_id)

    factoryQuery = db.query(Factory).filter(Factory.companyId == company_id)

    employee_ids = [e.id for e in employeesQuery]

    factory_ids = [f.id for f in factoryQuery]

    distancesEmToFa = db.query(EmployeeToFactoryDistance).filter(
        EmployeeToFactoryDistance.employeeId.in_(employee_ids),
        EmployeeToFactoryDistance.factoryId.in_(factory_ids)
    ).all()

    distancesFaToFa = db.query(FactoryDistance).filter(
        FactoryDistance.factory_from_id.in_(factory_ids),
        FactoryDistance.factory_to_id.in_(factory_ids)
    ).all()

    blockedTimes = db.query(EmployeeBlockTime).filter(
        EmployeeBlockTime.employee_id.in_(employee_ids)
    ).all()

    employees = []
    em_locations = []
    fa_locations = []
    jobs = []

    for e in employeesQuery:
        employees.append({
            "employee_id": f"em_{e.id}",  # e.id là int → cần str
            "name": e.fullName,
            "skills": e.employeeSkillList,  "specialized": [
                "SpecificSkills"
            ]
        })

        # em_locations.append({
        #     "location_id": f"lo_em_{e.id}",
        #     "employee_id": f"em_{e.id}",  # e.id là int → cần str

        # })

    for fa in factoryQuery:
        fa_locations.append({
            "location_id": f"lo_fa_{fa.id}",
            "employee_id": ""
        })

    jobQuery = db.query(JobByEmployee).filter(
        JobByEmployee.companyId == company_id)

    for job in jobQuery:
        jobs.append({
            "job_duration": job.duration,
            "job_type": job.skillNeeded,
            "job_id": f"jo_{job.id}",
            "expected_date": weekday_to_date_this_week(job.expected_weekday).date(),
            "location_id": f"lo_fa_{job.factoryId}",
            "shipment_date":  weekday_to_date_this_week(job.expected_weekday).date()
        })

    # for em in employees:
    #     for fa_lo in fa_locations:
    #         distances.append({
    #             "hours": 2,
    #             "measure_point":  em["employee_id"],
    #             "reference_point": fa_lo["location_id"]

    #         })
    distance_em_to_fa_map = {
        (d.employeeId, d.factoryId): d.travel_time_hours
        for d in distancesEmToFa
    }

    distance_fa_to_fa_map = {
        (d.factory_from_id, d.factory_to_id): d.travel_time_hours
        for d in distancesFaToFa
    }

    result = []

    for employee in employeesQuery:
        for factory in factoryQuery:
            travel_time = distance_em_to_fa_map.get(
                (employee.id, factory.id),
                1  # 👈 default nếu chưa có
            )

            result.append({
                "hours": travel_time,
                "measure_point": f"em_{employee.id}",
                "reference_point": f"lo_fa_{factory.id}",
            })

    for i, fa_from in enumerate(factoryQuery):
        for fa_to in factoryQuery[i + 1:]:
            travel_time = distance_fa_to_fa_map.get(
                (fa_from.id, fa_to.id),
                0
            )

            result.append({
                "hours": travel_time,
                "measure_point": f"lo_fa_{fa_from.id}",
                "reference_point": f"lo_fa_{fa_to.id}",
            })

    return {"employees": employees, "locations": em_locations + fa_locations, "jobs": jobs, "distances": result, "blocked_times": []}


@router.post("/companies/{company_id}/schedule-job")
def getScheduleJob(company_id: int,
                   db: Session = Depends(get_db)):
    payload = getJobGeneral(company_id, db)

    payload_json = jsonable_encoder(payload)

    schedule = Employee_Scheduling_Problems(payload_json)["data"]
    print(schedule)

    for em in schedule:
        employee_id = em["employee_id"].split("_", 1)[1]

        for job in em["jobs"]:
            job_id = job["job_id"].split("_", 1)[1]
            factory_id = job["location_id"].split("_", 1)[1]
