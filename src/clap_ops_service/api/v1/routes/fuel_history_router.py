from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import require_fleet_role
from clap_ops_service.api.v1.schemas.fuel_history import (
    FuelHistoryCreate,
    FuelHistoryList,
    FuelHistoryResponse,
    FuelHistoryUpdate,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Fleet
from clap_ops_service.services.exceptions import ConflictError, NotFoundError
from clap_ops_service.services.fuel_history_service import FuelHistoryService
from .http_exceptions import conflict, not_found

fuel_history_router = APIRouter(
    prefix="/fuel-history",
    tags=["fuel-history"],
)


@fuel_history_router.post(
    "",
    response_model=FuelHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_fuel_entry(
    entry: FuelHistoryCreate,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MEMBER")),
) -> FuelHistoryResponse:
    try:
        return FuelHistoryService(db).add_fuel_entry(fleet.id, entry)
    except NotFoundError as error:
        raise not_found(error) from error
    except ConflictError as error:
        raise conflict(error) from error


@fuel_history_router.get("", response_model=FuelHistoryList)
def list_fuel_history(
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MEMBER")),
) -> FuelHistoryList:
    return FuelHistoryList(
        entries=FuelHistoryService(db).list_fuel_history(fleet.id)
    )


@fuel_history_router.get("/{entry_id}", response_model=FuelHistoryResponse)
def get_fuel_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MEMBER")),
) -> FuelHistoryResponse:
    try:
        return FuelHistoryService(db).get_fuel_entry(fleet.id, entry_id)
    except NotFoundError as error:
        raise not_found(error) from error


@fuel_history_router.patch("/{entry_id}", response_model=FuelHistoryResponse)
def update_fuel_entry(
    entry_id: UUID,
    entry: FuelHistoryUpdate,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MANAGER")),
) -> FuelHistoryResponse:
    try:
        return FuelHistoryService(db).update_fuel_entry(
            fleet.id,
            entry_id,
            entry,
        )
    except NotFoundError as error:
        raise not_found(error) from error
    except ConflictError as error:
        raise conflict(error) from error


@fuel_history_router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_fuel_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MANAGER")),
) -> None:
    try:
        FuelHistoryService(db).delete_fuel_entry(fleet.id, entry_id)
    except NotFoundError as error:
        raise not_found(error) from error
