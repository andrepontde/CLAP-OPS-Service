from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import (
    require_fleet_role,
)
from clap_ops_service.api.v1.schemas.operator import (
    OperatorCreate,
    OperatorList,
    OperatorResponse,
    OperatorUpdate,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Fleet
from clap_ops_service.services.exceptions import ConflictError, NotFoundError
from clap_ops_service.services.operator_service import OperatorService
from .http_exceptions import conflict, not_found

operator_router = APIRouter(prefix="/operators", tags=["operators"])


@operator_router.post(
    "", response_model=OperatorResponse, status_code=status.HTTP_201_CREATED
)
def create_operator(
    operator: OperatorCreate,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MANAGER")),
) -> OperatorResponse:
    try:
        return OperatorService(db).create_operator(fleet.id, operator)
    except ConflictError as error:
        raise conflict(error) from error


@operator_router.get("", response_model=OperatorList)
def list_operators(
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MEMBER")),
) -> OperatorList:
    return OperatorList(
        operators=OperatorService(db).list_operators(fleet.id)
    )


@operator_router.get("/{operator_id}", response_model=OperatorResponse)
def get_operator(
    operator_id: UUID,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MEMBER")),
) -> OperatorResponse:
    try:
        return OperatorService(db).get_operator(fleet.id, operator_id)
    except NotFoundError as error:
        raise not_found(error) from error


@operator_router.patch("/{operator_id}", response_model=OperatorResponse)
def update_operator(
    operator_id: UUID,
    operator: OperatorUpdate,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MANAGER")),
) -> OperatorResponse:
    try:
        return OperatorService(db).update_operator(
            fleet.id,
            operator_id,
            operator,
        )
    except NotFoundError as error:
        raise not_found(error) from error
    except ConflictError as error:
        raise conflict(error) from error


@operator_router.delete(
    "/{operator_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_operator(
    operator_id: UUID,
    db: Session = Depends(get_db),
    fleet: Fleet = Depends(require_fleet_role("MANAGER")),
) -> None:
    try:
        OperatorService(db).delete_operator(fleet.id, operator_id)
    except NotFoundError as error:
        raise not_found(error) from error
