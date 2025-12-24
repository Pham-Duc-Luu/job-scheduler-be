from pydantic import BaseModel, EmailStr
from typing import Optional


class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None
    fax: Optional[str] = None
    owner: int
    domain: str


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None
    fax: Optional[str] = None
    equipementManagerId: Optional[int] = None


class CompanyRead(CompanyBase):
    id: int

    class Config:
        orm_mode = True
