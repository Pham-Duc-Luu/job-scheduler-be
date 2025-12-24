from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models
from app.schemas.location import LocationCreate, LocationUpdate


def create_location(db: Session, company_id: int, location: LocationCreate):
    db_location = models.Location(
        companyId=company_id,
        name=location.name,
        address=location.address,
        type=location.type
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_location(db: Session, company_id: int, location_id: int):
    location = db.query(models.Location).filter(
        models.Location.id == location_id,
        models.Location.companyId == company_id
    ).first()
    if not location:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy địa điểm trong công ty này")
    return location


def get_locations_by_company(db: Session, company_id: int):
    return db.query(models.Location).filter(
        models.Location.companyId == company_id
    ).all()


def update_location(db: Session, company_id: int, location_id: int, location_update: LocationUpdate):
    db_location = get_location(db, company_id, location_id)
    for key, value in location_update.dict(exclude_unset=True).items():
        setattr(db_location, key, value)
    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, company_id: int, location_id: int):
    db_location = get_location(db, company_id, location_id)
    db.delete(db_location)
    db.commit()
    return {"detail": f"Đã xóa địa điểm {location_id} của công ty {company_id}"}
