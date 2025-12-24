from fastapi import HTTPException
from app.models import Company, JobByEmployee
from sqlalchemy.orm import Session


def validate_job(job_id: int, company_id: int, db: Session):
    job = (
        db.query(JobByEmployee)
        .filter(
            JobByEmployee.id == job_id,
            JobByEmployee.companyId == company_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Công việc ID {job_id} không thuộc công ty."
        )

    return job


def validate_company(company_id: int, db: Session):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Công ty với ID {company_id} không tồn tại."
        )
    return company
