# crud/employee_factory_distance.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import EmployeeToFactoryDistance
from app.schemas.employee_distance import EmployeeFactoryDistanceCreate, EmployeeFactoryDistanceUpdate, EmployeeFactoryDistanceUpsert


def get_list(db: Session, company_id: int):
    return (
        db.query(EmployeeToFactoryDistance)
        .filter(EmployeeToFactoryDistance.companyId == company_id)
        .all()
    )


def get_by_id(db: Session, company_id: int, distance_id: int):
    return (
        db.query(EmployeeToFactoryDistance)
        .filter(
            EmployeeToFactoryDistance.id == distance_id,
            EmployeeToFactoryDistance.companyId == company_id,
        )
        .first()
    )


def create(
    db: Session,
    company_id: int,
    data: EmployeeFactoryDistanceCreate,
):
    obj = EmployeeToFactoryDistance(
        companyId=company_id,
        **data.model_dump(),
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def update(
    db: Session,
    obj: EmployeeToFactoryDistance,
    data: EmployeeFactoryDistanceUpdate,
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: EmployeeToFactoryDistance):
    db.delete(obj)
    db.commit()


def upsert(
    db: Session,
    company_id: int,
    payload: EmployeeFactoryDistanceUpsert,
):
    obj = (
        db.query(EmployeeToFactoryDistance)
        .filter(
            EmployeeToFactoryDistance.companyId == company_id,
            EmployeeToFactoryDistance.employeeId == payload.employeeId,
            EmployeeToFactoryDistance.factoryId == payload.factoryId,
        )
        .first()
    )

    if obj:
        # UPDATE
        obj.distance_km = payload.distance_km
        obj.travel_time_hours = payload.travel_time_hours
        action = "updated"
    else:
        # CREATE
        obj = EmployeeToFactoryDistance(
            companyId=company_id,
            employeeId=payload.employeeId,
            factoryId=payload.factoryId,
            distance_km=payload.distance_km,
            travel_time_hours=payload.travel_time_hours,
        )
        db.add(obj)
        action = "created"

    db.commit()
    db.refresh(obj)
    return obj, action
