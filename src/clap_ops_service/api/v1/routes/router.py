from fastapi import APIRouter

from .auth_router import auth_router
from .charging_history_router import charging_history_router
from .fleet_router import fleet_router
from .fuel_history_router import fuel_history_router
from .operator_router import operator_router
from .vehicle_router import vehicle_router

v1_router = APIRouter()
v1_router.include_router(auth_router)
v1_router.include_router(charging_history_router)
v1_router.include_router(fleet_router)
v1_router.include_router(fuel_history_router)
v1_router.include_router(operator_router)
v1_router.include_router(vehicle_router)
