# routers/employee_factory_distance.py
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Employee, EmployeeToFactoryDistance, Factory
from app.services import employee_factory_distance

from app.schemas.employee_distance import EmployeeFactoryDistanceByEmployeeResponse, EmployeeFactoryDistanceCreate, EmployeeFactoryDistanceResponse, EmployeeFactoryDistanceUpdate, EmployeeFactoryDistanceUpsert

router = APIRouter(
    prefix="/company/{companyId}/employee-factory-distances",
    tags=["Employee-Factory Distance"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=EmployeeFactoryDistanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_distance(
    companyId: int,
    payload: EmployeeFactoryDistanceCreate,
    db: Session = Depends(get_db),
):
    try:
        return employee_factory_distance.create(db, companyId, payload)
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Khoảng cách giữa nhân viên và nhà máy này đã tồn tại",
        )


@router.get(
    "",
    response_model=list[EmployeeFactoryDistanceResponse],
)
def list_distances(
    companyId: int,
    db: Session = Depends(get_db),
):
    return employee_factory_distance.get_list(db, companyId)


@router.get(
    "/{distanceId}",
    response_model=EmployeeFactoryDistanceResponse,
)
def get_distance(
    companyId: int,
    distanceId: int,
    db: Session = Depends(get_db),
):
    obj = employee_factory_distance.get_by_id(db, companyId, distanceId)
    if not obj:
        raise HTTPException(status_code=404, detail="Distance not found")
    return obj


@router.put(
    "/{distanceId}",
    response_model=EmployeeFactoryDistanceResponse,
)
def update_distance(
    companyId: int,
    distanceId: int,
    payload: EmployeeFactoryDistanceUpdate,
    db: Session = Depends(get_db),
):
    obj = employee_factory_distance.get_by_id(db, companyId, distanceId)
    if not obj:
        raise HTTPException(
            status_code=404,
            detail="Không tồn tại khoảng cách giữa nhân viên và nhà máy cần cập nhật",
        )

    return employee_factory_distance.update(db, obj, payload)


@router.delete(
    "/{distanceId}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_distance(
    companyId: int,
    distanceId: int,
    db: Session = Depends(get_db),
):
    obj = employee_factory_distance.get_by_id(db, companyId, distanceId)
    if not obj:
        raise HTTPException(
            status_code=404,
            detail="Không tồn tại khoảng cách giữa nhân viên và nhà máy cần xoá",
        )

    employee_factory_distance.delete(db, obj)


@router.post(
    "/upsert",
    response_model=EmployeeFactoryDistanceResponse,
)
def upsert_employee_factory_distance(
    companyId: int,
    payload: EmployeeFactoryDistanceUpsert,
    db: Session = Depends(get_db),
):

    if not db.query(Employee.id).filter(
        Employee.id == payload.employeeId,
        Employee.companyId == companyId,
    ).first():
        raise HTTPException(
            status_code=404,
            detail="Nhân viên không thuộc công ty này",
        )

    if not db.query(Factory.id).filter(
        Factory.id == payload.factoryId,
        Factory.companyId == companyId,
    ).first():
        raise HTTPException(
            status_code=404,
            detail="Nhà máy không thuộc công ty này",
        )

    obj, action = employee_factory_distance.upsert(db, companyId, payload)

    if action == "created":
        return obj
    else:
        return obj
