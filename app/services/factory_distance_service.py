# services/factory_distance_service.py

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import Factory, FactoryDistance
from app.schemas.factory_distance import FactoryDistanceCreate, FactoryDistanceUpdate


def validate_both_factories_belong_to_company(db: Session, company_id: int, f1: int, f2: int):
    factories = db.query(Factory).filter(Factory.id.in_([f1, f2])).all()

    if len(factories) != 2:
        raise HTTPException(status_code=404, detail="Factory không tồn tại.")

    for f in factories:
        if f.companyId != company_id:
            raise HTTPException(
                status_code=400,
                detail="Hai factory không thuộc cùng company."
            )


def create_factory_distance(company_id: int, data: FactoryDistanceCreate, db: Session):

    f1 = data.factory_from_id
    f2 = data.factory_to_id

    factory_from_id = min(f1, f2)
    factory_to_id = max(f1, f2)

    if factory_from_id == factory_to_id:
        raise HTTPException(
            status_code=400, detail="factory_from_id và factory_to_id không được trùng.")

    validate_both_factories_belong_to_company(
        db, company_id, factory_from_id, factory_to_id
    )

    # Kiểm tra trùng
    exists = db.query(FactoryDistance).filter(
        FactoryDistance.factory_from_id == factory_from_id,
        FactoryDistance.factory_to_id == factory_to_id
    ).first()

    if exists:
        raise HTTPException(400, "Khoảng cách giữa hai factory đã tồn tại.")

    record = FactoryDistance(
        companyId=company_id,
        factory_from_id=factory_from_id,
        factory_to_id=factory_to_id,
        distance_km=data.distance_km,
        travel_time_hours=data.travel_time_hours
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_factory_distances(company_id: int, db: Session):
    return db.query(FactoryDistance).filter(
        FactoryDistance.companyId == company_id
    ).all()


def get_factory_distance(company_id: int, distance_id: int, db: Session):
    record = db.query(FactoryDistance).options(
        joinedload(FactoryDistance.factory_from),
        joinedload(FactoryDistance.factory_to)
    ).filter(
        FactoryDistance.id == distance_id,
        FactoryDistance.companyId == company_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=404, detail="Factory distance không tồn tại.")

    return record


def update_factory_distance(company_id: int, distance_id: int, data: FactoryDistanceUpdate, db: Session):
    record = get_factory_distance(company_id, distance_id, db)

    if data.distance_km is not None:
        record.distance_km = data.distance_km

    if data.travel_time_hours is not None:
        record.travel_time_hours = data.travel_time_hours

    db.commit()
    db.refresh(record)
    return record


def delete_factory_distance(company_id: int, distance_id: int, db: Session):
    record = get_factory_distance(company_id, distance_id, db)
    db.delete(record)
    db.commit()
    return {"message": "Xóa thành công"}
