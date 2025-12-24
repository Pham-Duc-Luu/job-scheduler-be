from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.schemas.UserSchema import UserResponse
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services import company_service
from app.utils import get_current_user

router = APIRouter(prefix="/companies", tags=["Companies"])

# Dependency for DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[CompanyRead])
def read_companies_by_admin(
    current_user: UserResponse = Depends(get_current_user),
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Get all companies owned by a specific Admin.
    """
    companies = company_service.get_companies_by_admin(
        db, current_user.id, skip, limit)
    if not companies:
        raise HTTPException(
            status_code=404, detail="No companies found for this admin")
    return companies

# ✅ Create company by owner


@router.post("/", response_model=CompanyRead)
def create_company_by_owner(owner_id: int, company: CompanyCreate, db: Session = Depends(get_db)):
    """
    Create a company owned by a specific Admin (owner_id).
    """
    return company_service.create_company_by_owner(db, owner_id, company)


@router.get("/", response_model=List[CompanyRead])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return company_service.get_companies(db, skip, limit)


@router.get("/{company_id}", response_model=CompanyRead)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = company_service.get_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@router.put("/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, company_update: CompanyUpdate, db: Session = Depends(get_db)):
    db_company = company_service.update_company(db, company_id, company_update)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@router.delete("/{company_id}", response_model=CompanyRead)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    db_company = company_service.delete_company(db, company_id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company
