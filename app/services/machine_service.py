import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app import models
from app.schemas.machine import MachineCreate, MachineUpdate


def create_machine_in_company(db: Session, company_id: int, machine: MachineCreate):
    # Check company exists
    company = db.query(models.Company).filter(
        models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db_machine = models.Machine(
        name=machine.name,
        description=machine.description,
        companyId=company_id,
        type=machine.type,
        manual_url=machine.manual_url,
        vendor=machine.vendor,
        note=machine.note,
        code=str(uuid.uuid4())[:8]
    )
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine


def update_machine_in_company(db: Session, company_id: int, machine_id: int, machine_update: MachineUpdate):
    db_machine = db.query(models.Machine).filter(
        models.Machine.id == machine_id, models.Machine.companyId == company_id
    ).first()

    if not db_machine:
        raise HTTPException(
            status_code=404, detail="Machine not found for this company")

    if machine_update.name is not None:
        db_machine.name = machine_update.name
    if machine_update.description is not None:
        db_machine.description = machine_update.description

    db.commit()
    db.refresh(db_machine)
    return db_machine


def get_machines_in_company(db: Session, company_id: int):
    machines = db.query(models.Machine).filter(
        models.Machine.companyId == company_id).all()
    return machines
