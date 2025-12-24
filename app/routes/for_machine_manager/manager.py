from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models import Machine, MachineInFactory, RequestStatus
from app.schemas.machine import MachineBase
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/manager/machine", tags=["machine-manager"])


@router.get("/{machine_id}/company/{company_id}", response_model=MachineBase)
def get_machine_detail(machine_id: int, company_id: int, db: Session = Depends(get_db)):
    machine = (
        db.query(Machine)
        .filter(Machine.id == machine_id, Machine.companyId == company_id)
        .options(joinedload(Machine.machine_in_factories).joinedload(MachineInFactory.factory))
        .first()
    )

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    for mif in machine.machine_in_factories:
        print(mif)

    return machine  # thanks to orm_mode, Pydantic sẽ tự động serialize relationships


@router.patch("/{machine_id}/factory/{factory_id}/resolve/{resolve_status}")
def resolve_machine_request(
    machine_id: int,
    factory_id: int,
    resolve_status: RequestStatus,
    db: Session = Depends(get_db)
):
    mif = (
        db.query(MachineInFactory)
        .filter(
            MachineInFactory.machineId == machine_id,
            MachineInFactory.factoryId == factory_id
        )
        .first()
    )

    if not mif:
        raise HTTPException(
            status_code=404, detail="không thể tìm thấy request của máy")

    # update status
    mif.status = resolve_status
    db.commit()
    db.refresh(mif)

    return {
        "message": f"Request updated to {resolve_status}",
        "machineId": machine_id,
        "factoryId": factory_id,
        "status": mif.status,
    }
