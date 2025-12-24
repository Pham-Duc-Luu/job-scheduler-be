# routers/admin_factory_distance.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.factory_distance import FactoryDistanceCreate, FactoryDistanceResponse, FactoryDistanceUpdate
from app.services.factory_distance_service import create_factory_distance, delete_factory_distance, get_factory_distance, get_factory_distances, update_factory_distance

router = APIRouter(
    prefix="/company/{companyId}/factory-distance", tags=[" factory distance"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE
@router.post("/", response_model=FactoryDistanceResponse)
def create_distance(companyId: int, payload: FactoryDistanceCreate, db: Session = Depends(get_db)):
    return create_factory_distance(companyId, payload, db)


# LIST
@router.get("/", response_model=list[FactoryDistanceResponse])
def list_distances(companyId: int, db: Session = Depends(get_db)):
    return get_factory_distances(companyId, db)


# GET DETAIL
@router.get("/{distanceId}", response_model=FactoryDistanceResponse)
def get_distance(companyId: int, distanceId: int, db: Session = Depends(get_db)):
    return get_factory_distance(companyId, distanceId, db)


# UPDATE
@router.put("/{distanceId}", response_model=FactoryDistanceResponse)
def update_distance(companyId: int, distanceId: int, payload: FactoryDistanceUpdate, db: Session = Depends(get_db)):
    return update_factory_distance(companyId, distanceId, payload, db)


# DELETE
@router.delete("/{distanceId}")
def delete_distance(companyId: int, distanceId: int, db: Session = Depends(get_db)):
    return delete_factory_distance(companyId, distanceId, db)
