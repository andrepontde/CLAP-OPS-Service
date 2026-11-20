from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import get_current_admin
from clap_ops_service.api.v1.schemas.fleet import (
    FleetCreate,
    FleetList,
    FleetMembershipCreate,
    FleetResponse,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Admin
from clap_ops_service.services.exceptions import ConflictError, NotFoundError
from clap_ops_service.services.fleet_service import FleetService


fleet_router = APIRouter(prefix="/fleets", tags=["fleets"])


def require_superadmin(admin: Admin) -> None:
    if not admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required",
        )


@fleet_router.post(
    "",
    response_model=FleetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fleet(
    fleet_data: FleetCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> FleetResponse:
    require_superadmin(current_admin)
    try:
        return FleetService(db).create(fleet_data)
    except ConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@fleet_router.get("", response_model=FleetList)
def list_fleets(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> FleetList:
    return FleetList(
        fleets=FleetService(db).list_for_admin(current_admin)
    )


@fleet_router.put(
    "/{fleet_id}/memberships/{admin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def set_fleet_membership(
    fleet_id: UUID,
    admin_id: UUID,
    membership: FleetMembershipCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> None:
    require_superadmin(current_admin)
    try:
        FleetService(db).set_membership(
            fleet_id,
            admin_id,
            membership.role,
        )
    except NotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
