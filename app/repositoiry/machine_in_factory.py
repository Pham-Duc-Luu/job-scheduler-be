from sqlalchemy.orm import Session
from app.models import MachineInFactory, RequestStatus


def get_machines_in_factory(db: Session, factory_id: int, status: RequestStatus | None = None):
    query = db.query(MachineInFactory).filter(
        MachineInFactory.factoryId == factory_id)

    if status:
        query = query.filter(MachineInFactory.status == status)

    return query.all()
