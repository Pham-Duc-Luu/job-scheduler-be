from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app.schemas.factory import FactoryCreate, FactoryRead, FactoryUpdate, machineIdINnFactory
from app.services import factory_service

router = APIRouter(prefix="/factories", tags=["Factories by admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/company/{company_id}", response_model=FactoryRead)
def create_factory_in_company(company_id: int, factory: FactoryCreate, db: Session = Depends(get_db)):
    # tạo mới một factory
    factory = factory_service.create_factory_in_company(
        db, company_id, factory)

    return factory


@router.get("/company/{company_id}", response_model=List[FactoryRead])
def get_factories_by_company(company_id: int, db: Session = Depends(get_db)):
    return factory_service.get_factories_by_company(db, company_id)


@router.put("/{factory_id}", response_model=FactoryRead)
def update_factory(factory_id: int, factory_update: FactoryUpdate, db: Session = Depends(get_db)):
    return factory_service.update_factory(db, factory_id, factory_update)


@router.delete("/{factory_id}")
def delete_factory(factory_id: int, db: Session = Depends(get_db)):
    return factory_service.delete_factory(db, factory_id)


routerFactory = APIRouter(prefix="/admin/factory",)


@routerFactory.post("/{factory_id}/machine/{machine_id}", response_model=FactoryRead)
def add_machine_to_factory(factory_id: int, machine_id: int, db: Session = Depends(get_db)):
    """
    🏭 Thêm một máy vào nhà máy (mặc định `isActive = True`)
    """
    factory = factory_service.add_machine_to_factory(
        db, factory_id, machine_id)
    return factory


@routerFactory.put("/{factory_id}/machines", response_model=FactoryRead)
def update_machine_list(factory_id: int, machine_list: List[machineIdINnFactory], db: Session = Depends(get_db)):
    """
    Cập nhật toàn bộ danh sách máy của nhà máy
    """
    updated = factory_service.update_machine_list_in_factory_by_admin(
        db, factory_id, [m.dict() for m in machine_list]
    )
    return updated


@router.get(
    "/company/{company_id}/factory/{factory_id}",
    response_model=FactoryRead
)
def get_factory_detail(company_id: int, factory_id: int, db: Session = Depends(get_db)):
    return factory_service.get_factory_in_company(db, company_id, factory_id)


router.include_router(router=routerFactory)
