from fastapi import APIRouter
from .routes import router as requests_router

v1_router = APIRouter(prefix='/v1/carsdetails')
v1_router.include_router(requests_router)
