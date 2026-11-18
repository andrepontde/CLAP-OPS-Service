from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import (
    get_authorized_fleet,
    get_current_admin,
)
from clap_ops_service.api.v1.schemas.vehicle import (
    VehicleCreate,
    VehicleList,
    VehicleResponse,
    VehicleUpdate,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Admin, Fleet
from clap_ops_service.services.exceptions import ConflictError, NotFoundError
from clap_ops_service.services.vehicle_service import VehicleService
from .http_exceptions import conflict, not_found

vehicle_router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@vehicle_router.post(
    "", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED
)
def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
    fleet: Fleet = Depends(get_authorized_fleet),
) -> VehicleResponse:
    try:
        return VehicleService(db).create_vehicle(fleet.id, vehicle)
    except ConflictError as error:
        raise conflict(error) from error


@vehicle_router.get("", response_model=VehicleList)
def list_vehicles(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
    fleet: Fleet = Depends(get_authorized_fleet),
) -> VehicleList:
    return VehicleList(
        vehicles=VehicleService(db).list_vehicles(fleet.id)
    )


@vehicle_router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
    fleet: Fleet = Depends(get_authorized_fleet),
) -> VehicleResponse:
    try:
        return VehicleService(db).get_vehicle(fleet.id, vehicle_id)
    except NotFoundError as error:
        raise not_found(error) from error


@vehicle_router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: UUID,
    vehicle: VehicleUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
    fleet: Fleet = Depends(get_authorized_fleet),
) -> VehicleResponse:
    try:
        return VehicleService(db).update_vehicle(
            fleet.id,
            vehicle_id,
            vehicle,
        )
    except NotFoundError as error:
        raise not_found(error) from error
    except ConflictError as error:
        raise conflict(error) from error


@vehicle_router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
    fleet: Fleet = Depends(get_authorized_fleet),
) -> None:
    try:
        VehicleService(db).delete_vehicle(fleet.id, vehicle_id)
    except NotFoundError as error:
        raise not_found(error) from error
