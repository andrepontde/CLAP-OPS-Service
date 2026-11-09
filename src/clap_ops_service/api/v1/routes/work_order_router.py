from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.dependencies import get_current_admin
from clap_ops_service.api.v1.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderList,
    WorkOrderResponse,
    WorkOrderUpdate,
)
from clap_ops_service.database import get_db
from clap_ops_service.database.models import Admin
from clap_ops_service.services.work_order_service import WorkOrderService

work_order_router = APIRouter(prefix="/work-orders", tags=["work-orders"])


def _not_found(error: ValueError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


def _server_error(error: RuntimeError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(error),
    )


@work_order_router.post(
    "", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED
)
def create_work_order(
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> WorkOrderResponse:
    try:
        return WorkOrderService(db).create_work_order(work_order)
    except ValueError as error:
        raise _not_found(error) from error
    except RuntimeError as error:
        raise _server_error(error) from error


@work_order_router.get("", response_model=WorkOrderList)
def list_work_orders(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> WorkOrderList:
    return WorkOrderList(work_orders=WorkOrderService(db).list_work_orders())


@work_order_router.get("/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> WorkOrderResponse:
    try:
        return WorkOrderService(db).get_work_order(work_order_id)
    except ValueError as error:
        raise _not_found(error) from error


@work_order_router.patch(
    "/{work_order_id}", response_model=WorkOrderResponse
)
def update_work_order(
    work_order_id: UUID,
    work_order: WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> WorkOrderResponse:
    try:
        return WorkOrderService(db).update_work_order(work_order_id, work_order)
    except ValueError as error:
        raise _not_found(error) from error
    except RuntimeError as error:
        raise _server_error(error) from error


@work_order_router.delete(
    "/{work_order_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_work_order(
    work_order_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> None:
    try:
        WorkOrderService(db).delete_work_order(work_order_id)
    except ValueError as error:
        raise _not_found(error) from error
    except RuntimeError as error:
        raise _server_error(error) from error
