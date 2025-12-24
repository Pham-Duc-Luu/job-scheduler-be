from pydantic import BaseModel, EmailStr
from typing import Optional

# Base schema for shared fields


class AdminBase(BaseModel):
    email: EmailStr
    phoneNumber: Optional[str] = None
    name: str

# Schema for creating Admin


class AdminCreate(AdminBase):
    password: str

# Schema for updating Admin


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None

# Schema for reading Admin (response)


class AdminRead(AdminBase):
    id: int

    class Config:
        orm_mode = True
