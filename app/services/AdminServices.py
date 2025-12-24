from sqlalchemy.orm import Session
from app import models
from ..schemas import AdminSchema

# Hash password


# Create Admin


def create_admin(db: Session, admin: AdminSchema.AdminCreate):
    db_admin = models.Admin(
        email=admin.email,
        password=(admin.password),
        phoneNumber=admin.phoneNumber,
        name=admin.name
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

# Get Admin by ID


def get_admin(db: Session, admin_id: int):
    return db.query(models.Admin).filter(models.Admin.id == admin_id).first()

# Get all Admins


def get_admins(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Admin).offset(skip).limit(limit).all()

# Update Admin


def update_admin(db: Session, admin_id: int, admin_update: AdminSchema.AdminUpdate):
    db_admin = get_admin(db, admin_id)
    if not db_admin:
        return None
    for field, value in admin_update.dict(exclude_unset=True).items():
        if field == "password":
            value = (value)
        setattr(db_admin, field, value)
    db.commit()
    db.refresh(db_admin)
    return db_admin

# Delete Admin


def delete_admin(db: Session, admin_id: int):
    db_admin = get_admin(db, admin_id)
    if not db_admin:
        return None
    db.delete(db_admin)
    db.commit()
    return db_admin
