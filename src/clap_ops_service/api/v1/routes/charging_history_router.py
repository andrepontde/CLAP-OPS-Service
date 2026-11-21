from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import get_current_admin, require_fleet_role
from clap_ops_service.api.v1.schemas.charging_history import (
    ChargingHistoryCreate,
    ChargingHistoryList,
    ChargingHistoryResponse,
    ChargingHistoryUpdate,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Admin, Fleet
from clap_ops_service.services.charging_history_service import ChargingHistoryService
from clap_ops_service.services.exceptions import ConflictError, NotFoundError
from .http_exceptions import conflict, not_found

charging_history_router = APIRouter(
    prefix="/charging-history",
    tags=["charging-history"],
)


@charging_history_router.post(
    "",
    response_model=ChargingHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_charging_entry(
    entry: ChargingHistoryCreate,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MEMBER")),
    current_admin: Admin = Depends(get_current_admin),
) -> ChargingHistoryResponse:
    try:
        return ChargingHistoryService(db).add_charging_entry(
            fleet.id,
            entry,
            current_admin.name,
        )
    except NotFoundError as error:
        raise not_found(error) from error
    except ConflictError as error:
        raise conflict(error) from error


@charging_history_router.get("", response_model=ChargingHistoryList)
def list_charging_history(
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MEMBER")),
) -> ChargingHistoryList:
    return ChargingHistoryList(
        entries=ChargingHistoryService(db).list_charging_history(fleet.id)
    )


@charging_history_router.get(
    "/{entry_id}",
    response_model=ChargingHistoryResponse,
)
def get_charging_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MEMBER")),
) -> ChargingHistoryResponse:
    try:
        return ChargingHistoryService(db).get_charging_entry(fleet.id, entry_id)
    except NotFoundError as error:
        raise not_found(error) from error


@charging_history_router.patch(
    "/{entry_id}",
    response_model=ChargingHistoryResponse,
)
def update_charging_entry(
    entry_id: UUID,
    entry: ChargingHistoryUpdate,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MANAGER")),
) -> ChargingHistoryResponse:
    try:
        return ChargingHistoryService(db).update_charging_entry(
            fleet.id,
            entry_id,
            entry,
        )
    except NotFoundError as error:
        raise not_found(error) from error
    except ConflictError as error:
        raise conflict(error) from error


@charging_history_router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_charging_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MANAGER")),
) -> None:
    try:
        ChargingHistoryService(db).delete_charging_entry(fleet.id, entry_id)
    except NotFoundError as error:
        raise not_found(error) from error
