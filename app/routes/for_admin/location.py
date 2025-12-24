from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate
from app.services import location_service as location_crud

router = APIRouter(
    prefix="/companies/{company_id}/locations", tags=["Locations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=LocationRead)
def create_location(company_id: int, location: LocationCreate, db: Session = Depends(get_db)):
    return location_crud.create_location(db, company_id, location)


@router.get("/", response_model=List[LocationRead])
def list_locations(company_id: int, db: Session = Depends(get_db)):
    return location_crud.get_locations_by_company(db, company_id)


@router.get("/{location_id}", response_model=LocationRead)
def get_location(company_id: int, location_id: int, db: Session = Depends(get_db)):
    return location_crud.get_location(db, company_id, location_id)


@router.put("/{location_id}", response_model=LocationRead)
def update_location(company_id: int, location_id: int, location: LocationUpdate, db: Session = Depends(get_db)):
    return location_crud.update_location(db, company_id, location_id, location)


@router.delete("/{location_id}")
def delete_location(company_id: int, location_id: int, db: Session = Depends(get_db)):
    return location_crud.delete_location(db, company_id, location_id)
