from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import get_current_admin
from clap_ops_service.api.v1.schemas.vehicle import (
    VehicleCreate,
    VehicleList,
    VehicleResponse,
    VehicleUpdate,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Admin
from clap_ops_service.services.vehicle_service import VehicleService

vehicle_router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def _not_found(error: ValueError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@vehicle_router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> VehicleResponse:
    try:
        return VehicleService(db).create_vehicle(vehicle)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@vehicle_router.get("", response_model=VehicleList)
def list_vehicles(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> VehicleList:
    return VehicleList(vehicles=VehicleService(db).list_vehicles())


@vehicle_router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> VehicleResponse:
    try:
        return VehicleService(db).get_vehicle(vehicle_id)
    except ValueError as error:
        raise _not_found(error) from error


@vehicle_router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: UUID,
    vehicle: VehicleUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> VehicleResponse:
    try:
        return VehicleService(db).update_vehicle(vehicle_id, vehicle)
    except ValueError as error:
        if "not found" in str(error):
            raise _not_found(error) from error
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@vehicle_router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> None:
    try:
        VehicleService(db).delete_vehicle(vehicle_id)
    except ValueError as error:
        raise _not_found(error) from error
