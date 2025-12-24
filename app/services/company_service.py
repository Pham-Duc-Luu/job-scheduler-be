from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import models
from app.schemas.company import CompanyCreate, CompanyUpdate


def create_company(db: Session, company: CompanyCreate):
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def get_companies_by_admin(db: Session, admin_id: int, skip: int = 0, limit: int = 100):
    """
    Get all companies owned by a specific Admin (owner).
    """
    return (
        db.query(models.Company)
        .filter(models.Company.owner == admin_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_company_by_owner(db: Session, owner_id: int, company: CompanyCreate):
    # Verify owner exists
    owner = db.query(models.Admin).filter(models.Admin.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner (Admin) not found")

    # Create company under this owner
    db_company = models.Company(
        name=company.name,
        description=company.description,
        email=company.email,
        phoneNumber=company.phoneNumber,
        fax=company.fax,
        owner=owner_id,
        domain=company.domain
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def get_company(db: Session, company_id: int):
    return db.query(models.Company).filter(models.Company.id == company_id).first()


def get_companies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Company).offset(skip).limit(limit).all()


def update_company(db: Session, company_id: int, company_update: CompanyUpdate):
    db_company = get_company(db, company_id)
    if not db_company:
        return None
    for field, value in company_update.dict(exclude_unset=True).items():
        setattr(db_company, field, value)
    db.commit()
    db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int):
    db_company = get_company(db, company_id)
    if not db_company:
        return None
    db.delete(db_company)
    db.commit()
    return db_company
