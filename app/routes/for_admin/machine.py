from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app.schemas.machine import MachineCreate, MachineUpdate, MachineRead
from app.services import machine_service

router = APIRouter(prefix="/machines", tags=["Machines"])

# Dependency for DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/company/{company_id}", response_model=MachineRead)
def create_machine_in_company(company_id: int, machine: MachineCreate, db: Session = Depends(get_db)):
    return machine_service.create_machine_in_company(db, company_id, machine)


@router.put("/company/{company_id}/{machine_id}", response_model=MachineRead)
def update_machine_in_company(company_id: int, machine_id: int, machine: MachineUpdate, db: Session = Depends(get_db)):
    return machine_service.update_machine_in_company(db, company_id, machine_id, machine)


@router.get("/company/{company_id}", response_model=List[MachineRead])
def get_machines_in_company(company_id: int, db: Session = Depends(get_db)):
    return machine_service.get_machines_in_company(db, company_id)
