import asyncio
from app.middleware import AuthMiddleware
from app.routes.for_admin import company, job_operater, em_to_factory_distance,  employee, factory, admin_factory_distance, machine, factoryCycle, location, job
from app.routes import catalog, schedula_gen, admin
from app.routes.employee import employee_route
from fastapi import APIRouter, FastAPI, Request
from . import models
from starlette.middleware.cors import CORSMiddleware
from app.routes.company import route as CompanyRoute
from app.routes.company.employee import auth_em
from app.routes.for_machine_manager import manager
from .database import engine

app = FastAPI(title="Factory Scheduler API")


# Create tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Factory Scheduler API")

AdminRouter = APIRouter(prefix="/admin")

AdminRouter.include_router(company.router)
AdminRouter.include_router(employee.router)
AdminRouter.include_router(factory.router)
AdminRouter.include_router(machine.router)
AdminRouter.include_router(location.router)
AdminRouter.include_router(catalog.router)
AdminRouter.include_router(job_operater.router)
AdminRouter.include_router(job.router)
AdminRouter.include_router(factoryCycle.router)
AdminRouter.include_router(admin_factory_distance.router)
AdminRouter.include_router(em_to_factory_distance.router)


app.include_router(AdminRouter)
app.include_router(CompanyRoute.router)
app.include_router(manager.router)

app.add_middleware(AuthMiddleware.AuthMiddleware)

app.include_router(admin.router)
app.include_router(schedula_gen.router)
app.include_router(employee_route.router)

app.include_router(prefix="/auth", router=auth_em.router)


@app.get("/")
def read_root():
    return {"message": "Factory Scheduler API is running!"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✔ MUST be explicit

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_delay_middleware(request: Request, call_next):
    await asyncio.sleep(0)  # simulate 1-second internet delay
    response = await call_next(request)
    return response
