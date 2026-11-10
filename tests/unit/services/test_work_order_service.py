from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest
from psycopg.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError

from clap_ops_service.api.v1.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderUpdate,
)
from clap_ops_service.database.models import WorkOrder
from clap_ops_service.services.work_order_service import WorkOrderService


def work_order_create() -> WorkOrderCreate:
    return WorkOrderCreate(
        vehicle_id=uuid4(),
        title="Oil change",
        issue_description="Replace engine oil and filter",
        scheduled_start=datetime(2026, 11, 10, 9, tzinfo=timezone.utc),
    )


def test_create_work_order_adds_commits_refreshes_and_returns_work_order(
    db_session: Mock,
) -> None:
    result = WorkOrderService(db_session).create_work_order(work_order_create())

    assert isinstance(result, WorkOrder)
    assert result.title == "Oil change"
    assert result.status == "OPEN"
    db_session.add.assert_called_once_with(result)
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(result)


def test_create_work_order_reports_missing_vehicle(db_session: Mock) -> None:
    db_session.commit.side_effect = IntegrityError(
        "insert work order", {}, ForeignKeyViolation("vehicle_id")
    )

    with pytest.raises(ValueError, match="Vehicle not found"):
        WorkOrderService(db_session).create_work_order(work_order_create())

    db_session.rollback.assert_called_once_with()
    db_session.refresh.assert_not_called()


def test_update_work_order_changes_only_supplied_fields(db_session: Mock) -> None:
    work_order_id = uuid4()
    work_order = WorkOrder(
        id=work_order_id,
        **work_order_create().model_dump(exclude={"created_at"}),
    )
    db_session.query.return_value.filter.return_value.first.return_value = work_order

    result = WorkOrderService(db_session).update_work_order(
        work_order_id, WorkOrderUpdate(status="COMPLETED")
    )

    assert result.status == "COMPLETED"
    assert result.title == "Oil change"
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(work_order)


def test_update_work_order_reports_missing_vehicle(db_session: Mock) -> None:
    work_order_id = uuid4()
    work_order = WorkOrder(
        id=work_order_id,
        **work_order_create().model_dump(exclude={"created_at"}),
    )
    db_session.query.return_value.filter.return_value.first.return_value = work_order
    db_session.commit.side_effect = IntegrityError(
        "update work order", {}, ForeignKeyViolation("vehicle_id")
    )

    with pytest.raises(ValueError, match="Vehicle not found"):
        WorkOrderService(db_session).update_work_order(
            work_order_id, WorkOrderUpdate(vehicle_id=uuid4())
        )

    db_session.rollback.assert_called_once_with()
    db_session.refresh.assert_not_called()


def test_get_work_order_raises_when_missing(db_session: Mock) -> None:
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Work order not found"):
        WorkOrderService(db_session).get_work_order(uuid4())


def test_delete_work_order_deletes_and_commits(db_session: Mock) -> None:
    work_order = WorkOrder(
        id=uuid4(),
        **work_order_create().model_dump(exclude={"created_at"}),
    )
    db_session.query.return_value.filter.return_value.first.return_value = work_order

    WorkOrderService(db_session).delete_work_order(work_order.id)

    db_session.delete.assert_called_once_with(work_order)
    db_session.commit.assert_called_once_with()
