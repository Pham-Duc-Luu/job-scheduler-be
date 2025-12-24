from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from app import models
from app.database import SessionLocal
from app.utils import create_access_token
from ..services import AdminServices

from ..schemas import AdminSchema, UserSchema

router = APIRouter(prefix="/admins", tags=["Admins"])

# Dependency to get DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create Admin


@router.post("/sign-up",
             #  response_model=AdminSchema.AdminRead
             )
def create_admin(admin: AdminSchema.AdminCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(models.Admin).filter(
        models.Admin.email == admin.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    newAdmin = AdminServices.create_admin(db, admin)

    jwtAdminInfo = UserSchema.UserResponse(
        id=newAdmin.id,
        email=newAdmin.email, name=newAdmin.name, phoneNumber=newAdmin.phoneNumber,  role="admin")

    token = create_access_token(jwtAdminInfo.to_payload())

    # Set cookie
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,      # Đặt True nếu dùng HTTPS
        samesite="lax",
        max_age=7 * 24 * 3600
    )

    return {
        "detail": "signed up"
    }

# Get all Admins


@router.post("/sign-in",
             #  response_model=AdminSchema.AdminRead
             )
def admin_sign_in(login: AdminSchema.AdminLogin, response: Response, db: Session = Depends(get_db)):
    """
    Sign in an Admin without password encryption.
    """
    admin = db.query(models.Admin).filter(
        models.Admin.email == login.email).first()
    if not admin or admin.password != login.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Sai email hoặc mất khẩu")
    jwtAdminInfo = UserSchema.UserResponse(
        id=admin.id,
        email=admin.email, name=admin.name, phoneNumber=admin.phoneNumber,  role="admin")

    token = create_access_token(jwtAdminInfo.to_payload())

    # Set cookie
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,      # Đặt True nếu dùng HTTPS
        samesite="lax",
        max_age=7 * 24 * 3600
    )
    return {
        "detail": "signed in"
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    # Remove the cookie by setting it to empty and expired
    response.delete_cookie(key="token", path="/")
    return {"detail": "logged out"}

# Get all Admins


@router.get("/", response_model=List[AdminSchema.AdminRead])
def read_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AdminServices.get_admins(db, skip, limit)

# Get Admin by ID


@router.get("/{admin_id}", response_model=AdminSchema.AdminRead)
def read_admin(admin_id: int, db: Session = Depends(get_db)):
    db_admin = AdminServices .get_admin(db, admin_id)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin

# Update Admin


@router.put("/{admin_id}", response_model=AdminSchema.AdminRead)
def update_admin(admin_id: int, admin_update: AdminSchema.AdminUpdate, db: Session = Depends(get_db)):
    db_admin = AdminServices .update_admin(db, admin_id, admin_update)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin

# Delete Admin


@router.delete("/{admin_id}", response_model=AdminSchema.AdminRead)
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    db_admin = AdminServices .delete_admin(db, admin_id)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin
