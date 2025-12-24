from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import Machine, Employee, Factory, MachineInFactory, RequestStatus
from app.database import SessionLocal
from app.schemas.UserSchema import UserResponse
from app.schemas.factory import MachineRequestInFactory
from app.utils import get_current_user
from sqlalchemy.exc import IntegrityError
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# tạo request


@router.post("/{company_id}/factory/{factory_id}/request_machine/{machine_id}", response_model=dict)
def create_machine_request(factory_id: int, machine_id: int,
                           company_id: int,
                           current_user: UserResponse = Depends(
                               get_current_user),
                           db: Session = Depends(get_db)):
    factory = db.query(Factory).filter(
        Factory.id == factory_id and Factory.companyId == company_id).first()

    machineInCompany = db.query(Machine).filter(
        Machine.id == machine_id and Machine.companyId == company_id).first()

    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    if not machineInCompany:
        raise HTTPException(
            status_code=404, detail="Máy móc không thể tìm thấy")

    request = MachineInFactory(
        factoryId=factory.id,
        machineId=machineInCompany.id,
        companyId=company_id,
        status=RequestStatus.pending
    )

    db.add(request)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máy đã tồn tại trong factory này"
        )

    db.refresh(request)
    return {"message": "Request created", "request_id":     request.id}


class MachineListRequest(BaseModel):
    machineIds: List[int]


@router.post("/{company_id}/factory/{factory_id}/request_machines", response_model=dict)
def create_machine_requests(
    company_id: int,
    factory_id: int,
    request_body: MachineListRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Kiểm tra factory có thuộc công ty không
    factory = db.query(Factory).filter(
        Factory.id == factory_id,
        Factory.companyId == company_id
    ).first()

    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    created = []
    skipped = []

    for machine_id in request_body.machineIds:
        # Kiểm tra máy có thuộc company không
        machine = db.query(Machine).filter(
            Machine.id == machine_id,
            Machine.companyId == company_id
        ).first()

        if not machine:
            skipped.append(
                {"machineId": machine_id, "reason": "Machine not found"})
            continue

        # Tạo bản ghi mới
        new_request = MachineInFactory(
            factoryId=factory_id,
            machineId=machine.id,
            companyId=company_id,
            status=RequestStatus.pending
        )

        db.add(new_request)

        try:
            db.commit()
            db.refresh(new_request)
            created.append(
                {"machineId": machine.id, "requestId": new_request.id})
        except IntegrityError:
            db.rollback()
            # Máy đã tồn tại → bỏ qua
            skipped.append(
                {"machineId": machine.id, "reason": "Already exists"})

    return {
        "message": "Processed machine requests",
        "created": created,
        "skipped": skipped
    }
# manager duyệt request


# @router.post("/request_machine/{request_id}/approve", response_model=dict)
# def approve_machine_request(request_id: int, approve: bool, comment: str = None,  current_employee: UserResponse = Depends(
#         get_current_user), db: Session = Depends(get_db)):

#     request = db.query(MachineRequest).filter(
#         MachineRequest.id == request_id).first()
#     if not request:
#         raise HTTPException(status_code=404, detail="Request not found")

#     # kiểm tra employee có phải machineManager của công ty hay factory hay không
#     factory_manager = request.factory.manager
#     if current_employee.id != factory_manager.id:
#         raise HTTPException(
#             status_code=403, detail="Not authorized to approve this request")

#     request.status = RequestStatus.APPROVED if approve else RequestStatus.REJECTED
#     request.managerComment = comment
#     db.commit()
#     db.refresh(request)
#     return {"message": f"Request {'approved' if approve else 'rejected'}"}
