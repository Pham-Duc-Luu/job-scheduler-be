from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app import models
from app.schemas.employee import EmployeeRead, map_employee_to_read
from app.schemas.factory import FactoryCreate, FactoryRead, FactoryUpdate, machineIdINnFactory
from app.schemas.location import LocationCreate
from app.schemas.machine import MachineRead
from app.services import location_service


def create_factory_in_company(db: Session, company_id: int, factory: FactoryCreate):

    # Nếu chưa có locationId, tạo một Location mới
    location_id = factory.locationId
    # Kiểm tra công ty có tồn tại không

    company = db.query(models.Company).filter(
        models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Không tìm thấy công ty")

    # Kiểm tra vị trí đã được gán cho nhà máy khác chưa
    existing_location = db.query(models.Factory).filter(
        models.Factory.locationId == location_id
    ).first()

    if existing_location:
        raise HTTPException(
            status_code=400,
            detail="Vị trí này đã được gán cho một nhà máy khác"
        )

    # Kiểm tra người quản lý nhà máy đã được gán chưa
    if factory.factoryManager:
        existing_manager = db.query(models.Factory).filter(
            models.Factory.factoryManager == factory.factoryManager
        ).first()
        if existing_manager:
            raise HTTPException(
                status_code=400,
                detail="Nhân viên này đã được gán làm quản lý cho một nhà máy khác"
            )

    if not location_id:
        location_data = LocationCreate(
            name=factory.name,
            address=None,
            companyId=company_id,
        )
        location = location_service.create_location(
            db=db, company_id=company_id, location=location_data)
        location_id = location.id
    # Tạo Factory
    db_factory = models.Factory(
        companyId=company_id,
        name=factory.name,
        description=factory.description,
        locationId=location_id,
        factoryManager=factory.factoryManager
    )

    db.add(db_factory)
    db.commit()
    db.refresh(db_factory)

    return db_factory


def get_factories_by_company(db: Session, company_id: int):
    factories = db.query(models.Factory).options(
        joinedload(models.Factory.manager)
    ).filter(models.Factory.companyId == company_id).all()
    return factories


def update_factory(db: Session, factory_id: int, factory_update: FactoryUpdate):
    db_factory = db.query(models.Factory).filter(
        models.Factory.id == factory_id).first()
    if not db_factory:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà máy")

    # Kiểm tra trùng vị trí
    if factory_update.locationId and factory_update.locationId != db_factory.locationId:
        existing = db.query(models.Factory).filter(
            models.Factory.locationId == factory_update.locationId).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Vị trí này đã được gán cho một nhà máy khác"
            )

    # Kiểm tra trùng quản lý nhà máy
    if factory_update.factoryManager and factory_update.factoryManager != db_factory.factoryManager:
        existing = db.query(models.Factory).filter(
            models.Factory.factoryManager == factory_update.factoryManager).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Nhân viên này đã được gán làm quản lý cho một nhà máy khác"
            )

    for field, value in factory_update.dict(exclude_unset=True).items():
        setattr(db_factory, field, value)

    db.commit()
    db.refresh(db_factory)
    return db_factory


def delete_factory(db: Session, factory_id: int):
    db_factory = db.query(models.Factory).filter(
        models.Factory.id == factory_id).first()
    if not db_factory:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy nhà máy cần xóa")

    db.delete(db_factory)
    db.commit()
    return {"detail": f"Đã xóa nhà máy có ID {factory_id} thành công"}


def add_machine_to_factory_by_admin(db: Session, factory_id: int, machine_id: int):
    # Kiểm tra nhà máy có tồn tại không
    factory = db.query(models.Factory).filter(
        models.Factory.id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà máy")

    # Kiểm tra máy có tồn tại không
    machine = db.query(models.Machine).filter(
        models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Không tìm thấy máy")

    # Nếu chưa có danh sách máy thì khởi tạo
    if not factory.machineIdList:
        factory.machineIdList = []

    # Kiểm tra máy đã được thêm chưa
    existing = next(
        (m for m in factory.machineIdList if m["machineId"] == str(machine_id)), None)
    if existing:
        raise HTTPException(
            status_code=400, detail="Máy này đã được thêm vào nhà máy")

    # Thêm máy vào danh sách
    factory.machineIdList.append({
        "machineId": str(machine_id),
        "isActive": True
    })

    db.add(factory)
    db.commit()
    db.refresh(factory)

    return factory


def update_machine_list_in_factory_by_admin(
    db: Session,
    factory_id: int,
    machine_list: machineIdINnFactory  # [{machineId: int, isActive: bool}]
):
    # Kiểm tra nhà máy có tồn tại không
    factory = db.query(models.Factory).filter(
        models.Factory.id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà máy")

    # Validate danh sách input
    if not isinstance(machine_list, list):
        raise HTTPException(
            status_code=400,
            detail="Danh sách máy không hợp lệ"
        )

    updated_list = []

    for item in machine_list:
        machine_id = item.get("machineId")
        is_active = item.get("isActive")

        if machine_id is None:
            raise HTTPException(
                status_code=400,
                detail="Thiếu machineId trong danh sách máy"
            )

        # validate isActive
        if is_active is None:
            raise HTTPException(
                status_code=400, detail=f"Thiếu trạng thái isActive cho máy {machine_id}"
            )

        # Kiểm tra máy có tồn tại không
        machine = db.query(models.Machine).filter(
            models.Machine.id == machine_id).first()
        if not machine:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy máy có ID {machine_id}"
            )

        updated_list.append({
            "machineId": int(machine_id),
            "isActive": bool(is_active)
        })

    # Gán danh sách mới
    factory.machineIdList = updated_list

    db.add(factory)
    db.commit()
    db.refresh(factory)

    return factory


def get_factory_in_company(db: Session, company_id: int, factory_id: int):
    factory = db.query(models.Factory).options(
        joinedload(models.Factory.machines_in_factory).joinedload(
            models.MachineInFactory.machine)
    ).filter(
        models.Factory.id == factory_id,
        models.Factory.companyId == company_id
    ).first()

    # for mif in factory.machines_in_factory:
    #     print(mif.machine.code)

    if not factory:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy nhà máy trong công ty này")

    machines = []

    # if factory.machineIdList:
    # Lấy danh sách machineId
    # machine_id_map = {int(item["machineId"]): item["isActive"]
    #                   for item in factory.machineIdList}
    # machine_ids = list(machine_id_map.keys())

    # # Lấy thông tin máy từ DB
    # db_machines = db.query(models.Machine).filter(
    #     models.Machine.id.in_(machine_ids)
    # ).all()

    # Map isActive vào MachineRead
    for mif in factory.machines_in_factory:
        m = mif.machine
        print(m.code)

        machines.append(
            MachineRead(
                id=m.id,
                companyId=m.companyId,
                code=m.code,
                name=m.name,
                description=m.description,
                status=mif.status
            )
        )

    # Trả về đúng schema FactoryRead
    return FactoryRead(
        id=factory.id,
        companyId=factory.companyId,
        name=factory.name,
        description=factory.description,
        factoryManager=factory.factoryManager,
        # machineIdList=factory.machineIdList,
        manager=map_employee_to_read(
            factory.manager) if factory.manager else None,

        machines=machines
    )
