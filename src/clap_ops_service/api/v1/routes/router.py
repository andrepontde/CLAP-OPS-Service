from fastapi import APIRouter

from .auth_router import auth_router
from .operator_router import operator_router
from .vehicle_router import vehicle_router

v1_router = APIRouter()
v1_router.include_router(auth_router)
v1_router.include_router(operator_router)
v1_router.include_router(vehicle_router)
