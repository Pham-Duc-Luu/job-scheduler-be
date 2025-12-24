from sqlalchemy import and_
from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Factory, FactoryCycle, JobByMachine, JobByMachineOperate
from app.schemas.JobOperater import BatchJobOpTimeUpdate
from app.schemas.factoryCycle import FactoryCycleCreate, FactoryCycleResponse, FactoryCycleUpdate
from app.services.job_service import validate_cycle, validate_factory


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_factory_or_404(db: Session, companyId: int, factoryId: int):
    factory = (
        db.query(Factory)
        .filter(Factory.id == factoryId, Factory.companyId == companyId)
        .first()
    )
    if not factory:
        raise HTTPException(404, "Factory not found in this company")
    return factory


router = APIRouter(
    prefix="/company/{companyId}/factory/{factoryId}/cycle",
    tags=["Factory-Cycle"])


@router.get("", response_model=list[FactoryCycleResponse])
def list_cycles(companyId: int, factoryId: int, db: Session = Depends(get_db)):
    get_factory_or_404(db, companyId, factoryId)
    cycles = (
        db.query(FactoryCycle)
        .filter(FactoryCycle.factoryId == factoryId)
        .order_by(FactoryCycle.id.desc())
        .all()
    )
    return cycles


@router.get("/{cycleId}", response_model=FactoryCycleResponse)
def get_cycle(companyId: int, factoryId: int, cycleId: int, db: Session = Depends(get_db)):
    get_factory_or_404(db, companyId, factoryId)

    cycle = (
        db.query(FactoryCycle)
        .filter(FactoryCycle.id == cycleId, FactoryCycle.factoryId == factoryId)
        .first()
    )
    if not cycle:
        raise HTTPException(404, "FactoryCycle not found")
    return cycle


@router.post("", response_model=FactoryCycleResponse)
def create_cycle(
    companyId: int,
    factoryId: int,
    payload: FactoryCycleCreate,
    db: Session = Depends(get_db),
):
    get_factory_or_404(db, companyId, factoryId)

    # RULE: chỉ được tạo cycle nếu không có cycle đang active
#     active_cycle = (
#         db.query(FactoryCycle)
#         .filter(
#             FactoryCycle.factoryId == factoryId,
#             FactoryCycle.status != "completed"
#         )
#         .first()
#     )
#     if active_cycle:
#         raise HTTPException(
#             400, "Cannot create new cycle until current cycle is completed")

    cycle = FactoryCycle(
        factoryId=factoryId,
        name=payload.name,
        description=payload.description,
        startTime=payload.startTime,
        endTime=payload.endTime,
        status=payload.status,
    )
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.put("/{cycleId}", response_model=FactoryCycleResponse)
def update_cycle(
    companyId: int,
    factoryId: int,
    cycleId: int,
    payload: FactoryCycleUpdate,
    db: Session = Depends(get_db),
):
    get_factory_or_404(db, companyId, factoryId)

    cycle = (
        db.query(FactoryCycle)
        .filter(FactoryCycle.id == cycleId, FactoryCycle.factoryId == factoryId)
        .first()
    )
    if not cycle:
        raise HTTPException(404, "FactoryCycle not found")

    update_data = payload.dict(exclude_unset=True)

    # cập nhật các field
    for key, value in update_data.items():
        if value is not None:
            setattr(cycle, key, value)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.delete("/{cycleId}")
def delete_cycle(companyId: int, factoryId: int, cycleId: int, db: Session = Depends(get_db)):
    get_factory_or_404(db, companyId, factoryId)

    cycle = (
        db.query(FactoryCycle)
        .filter(FactoryCycle.id == cycleId, FactoryCycle.factoryId == factoryId)
        .first()
    )
    if not cycle:
        raise HTTPException(404, "FactoryCycle not found")

    db.delete(cycle)
    db.commit()
    return {"message": "Deleted successfully"}


@router.put("/{cycleId}/job-ops/time")
def update_job_ops_time_in_cycle(
        companyId: int,
    factoryId: int,
    cycleId: int,
    data: BatchJobOpTimeUpdate = Body(...),
    db: Session = Depends(get_db),
):
    validate_factory(db, companyId, factoryId)
    validate_cycle(db, factoryId, cycleId)

    if not data.items:
        return {"detail": "No job operations to update"}

    # 1️⃣ Lấy jobId hợp lệ trong cycle
    valid_job_ids = {
        row.id
        for row in db.query(JobByMachine.id)
        .filter(JobByMachine.factoryCycleId == cycleId)
        .all()
    }

    # 2️⃣ Validate input
    for item in data.items:
        if item.jobId not in valid_job_ids:
            raise HTTPException(
                status_code=400,
                detail=f"jobId {item.jobId} không thuộc cycle {cycleId}"
            )

        updated = db.query(JobByMachineOperate).filter(
            JobByMachineOperate.jobId == item.jobId,
            JobByMachineOperate.task_index == item.task_index
        ).update(
            {
                JobByMachineOperate.start: item.start,
                JobByMachineOperate.end: item.end,
            },
            synchronize_session=False
        )

        if updated == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy job_op (jobId={item.jobId}, task_index={item.task_index})"
            )

    # 3️⃣ Commit DUY NHẤT 1 lần
    db.commit()

    return {"detail": f"Updated {len(data.items)} job operations"}
