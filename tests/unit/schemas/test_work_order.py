from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from clap_ops_service.api.v1.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderResponse,
    WorkOrderUpdate,
)


def work_order_create() -> WorkOrderCreate:
    return WorkOrderCreate(
        vehicle_id=uuid4(),
        title="Oil change",
        issue_description="Replace engine oil and filter",
        scheduled_start=datetime(2026, 11, 10, 9, tzinfo=timezone.utc),
    )


def test_work_order_create_uses_open_as_the_default() -> None:
    work_order = work_order_create()

    assert work_order.status == "OPEN"
    assert work_order.scheduled_end is None


def test_work_order_create_rejects_unknown_status() -> None:
    data = work_order_create().model_dump()
    data["status"] = "REOPENED"

    with pytest.raises(ValidationError):
        WorkOrderCreate(**data)


def test_work_order_update_is_partial() -> None:
    update = WorkOrderUpdate(status="IN_PROGRESS")

    assert update.model_dump(exclude_unset=True) == {"status": "IN_PROGRESS"}


def test_work_order_response_reads_attributes_from_a_model() -> None:
    work_order = work_order_create()
    work_order_id = uuid4()
    created_at = datetime.now(timezone.utc)
    data = work_order.model_dump()
    data["created_at"] = created_at
    response = WorkOrderResponse.model_validate(
        SimpleNamespace(
            id=work_order_id,
            **data,
        )
    )

    assert response.id == work_order_id
    assert response.vehicle_id == work_order.vehicle_id
    assert response.created_at == created_at
