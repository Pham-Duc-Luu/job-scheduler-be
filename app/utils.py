from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from jose import jwt, JWTError
import random

from app.schemas.UserSchema import UserResponse


def generate_email(fullname: str, domain: str) -> str:
    """
    Generate email in format: <last_name>.<initials_of_other_names><4digit>@domain
    Example: "Pham Duc Luu" -> "luu.pd4821@example.com"
    """

    random_number = random.randint(1000, 9999)
    names = fullname.strip().split()
    if len(names) < 2:
        email = f"{names[0].lower()}.{random_number}@{domain}"
        return email

    # Last name
    last_name = names[-1].lower()

    # Initials of other names
    initials = "".join([n[0].lower() for n in names[:-1]])

    # Random 4-digit number

    email = f"{last_name}.{initials}{random_number}@{domain}"
    return email


SECRET_KEY = "your-secret-key"           # Đổi thành key mạnh hơn
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7   # 7 ngày


def create_access_token(data: dict, expires_delta: int = None):
    """
    Create JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token


def verify_token(token: str):
    """
    Decode & verify JWT. Raise error nếu token hỏng.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise Exception("Invalid or expired token")


def get_current_user(request: Request) -> UserResponse:
    user_dict = getattr(request.state, "user", None)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    # Chuyển dict thành UserResponse
    return UserResponse(**user_dict)


def model_to_dict(obj):
    print({c.name: getattr(obj, c.name) for c in obj.__table__.columns})


def weekday_to_date_this_week(
    expected_weekday: int,
    expand: int = 0
) -> datetime:
    """
    Convert expected_weekday (0=Mon..6=Sun)
    to datetime of that weekday in current week
    + expand weeks forward
    """

    if not 0 <= expected_weekday <= 6:
        raise ValueError("expected_weekday must be in range 0..6")

    if expand < 0:
        raise ValueError("expand must be >= 0")

    today = datetime.today()
    today_weekday = today.weekday()

    # Tìm ngày trong tuần hiện tại
    delta_days = expected_weekday - today_weekday
    print(delta_days)

    target_date = today + timedelta(days=delta_days)

    # Cộng thêm số tuần mở rộng

    target_date += timedelta(weeks=expand)
    print(target_date)

    return target_date.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
