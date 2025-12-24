# schemas/factory_distance.py

from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.employee import EmployeeRead


class FactoryDistanceCreate(BaseModel):
    factory_from_id: int
    factory_to_id: int
    distance_km: Optional[int] = None
    travel_time_hours: Optional[int] = None


class FactoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    factoryManager: Optional[int] = None
    # manager: Optional[EmployeeRead] = None

    class Config:
        orm_mode = True


class FactoryDistanceResponse(BaseModel):
    id: int
    factory_from_id: int
    factory_to_id: int
    distance_km: Optional[int] = None
    travel_time_hours: Optional[int] = None
    factory_from: Optional[FactoryBase] = None
    factory_to: Optional[FactoryBase] = None

    class Config:
        orm_mode = True


class FactoryDistanceUpdate(BaseModel):
    distance_km: int | None = None
    travel_time_hours: int | None = None
