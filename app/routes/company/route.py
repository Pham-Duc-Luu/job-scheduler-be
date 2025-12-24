from fastapi import APIRouter
from .employee import auth_em
from .factory import factory_manager
from .jobByEmployee import jobRouter

router = APIRouter()

router.include_router(prefix="/factory-manager",
                      router=factory_manager.router, tags=["factory manager"])

router.include_router(prefix="/company-task/manager",
                      tags=["Company Task Manager"],
                      router=jobRouter.router,)
