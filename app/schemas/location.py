from pydantic import BaseModel
from typing import Optional, Literal

from app.schemas.factory import FactoryRead


class LocationBase(BaseModel):
    name: str
    address: Optional[str] = None
    type: str


class LocationCreate(LocationBase):
    type: Literal["factory", "residence", "private_house"] = "factory"
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    type: Optional[Literal["factory", "residence", "private_house"]] = None


class LocationRead(LocationBase):
    id: int
    factory: Optional[FactoryRead] = None  # thêm dòng này

    class Config:
        orm_mode = True
