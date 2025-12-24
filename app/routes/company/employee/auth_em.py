

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal
from app.schemas import AdminSchema, UserSchema
from app.utils import create_access_token

router = APIRouter(prefix="/employee")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/sign-in",
             #  response_model=AdminSchema.AdminRead
             )
def admin_sign_in(login: UserSchema.LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Sign in an Admin without password encryption.
    """
    employee = db.query(models.Employee).filter(
        models.Employee.email == login.email).first()
    if not employee or employee.password != login.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Sai email hoặc mất khẩu")
    jwtAdminInfo = UserSchema.UserResponse(
        id=employee.id,
        email=employee.email, name=employee.fullName, phoneNumber=employee.phoneNumber,  role="staff")

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
