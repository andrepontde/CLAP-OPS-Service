from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import get_current_admin
from clap_ops_service.api.v1.schemas.operator import (
    OperatorCreate,
    OperatorList,
    OperatorResponse,
    OperatorUpdate,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Admin
from clap_ops_service.services.operator_service import OperatorService

operator_router = APIRouter(prefix="/operators", tags=["operators"])


def _not_found(error: ValueError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@operator_router.post(
    "", response_model=OperatorResponse, status_code=status.HTTP_201_CREATED
)
def create_operator(
    operator: OperatorCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> OperatorResponse:
    return OperatorService(db).create_operator(operator)


@operator_router.get("", response_model=OperatorList)
def list_operators(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> OperatorList:
    return OperatorList(operators=OperatorService(db).list_operators())


@operator_router.get("/{operator_id}", response_model=OperatorResponse)
def get_operator(
    operator_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> OperatorResponse:
    try:
        return OperatorService(db).get_operator(operator_id)
    except ValueError as error:
        raise _not_found(error) from error


@operator_router.patch("/{operator_id}", response_model=OperatorResponse)
def update_operator(
    operator_id: UUID,
    operator: OperatorUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> OperatorResponse:
    try:
        return OperatorService(db).update_operator(operator_id, operator)
    except ValueError as error:
        raise _not_found(error) from error


@operator_router.delete(
    "/{operator_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_operator(
    operator_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> None:
    try:
        OperatorService(db).delete_operator(operator_id)
    except ValueError as error:
        raise _not_found(error) from error
