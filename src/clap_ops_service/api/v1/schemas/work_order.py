from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


WORK_ORDER_STATUSES = "^(OPEN|IN_PROGRESS|COMPLETED|CANCELLED)$"


class WorkOrderBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: UUID
    title: str = Field(min_length=1, max_length=150)
    issue_description: str = Field(min_length=1)
    status: str = Field(default="OPEN", pattern=WORK_ORDER_STATUSES)
    scheduled_start: datetime
    scheduled_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    odometer_at_service: int | None = None
    created_at: datetime | None = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderResponse(WorkOrderBase):
    id: UUID


class WorkOrderList(BaseModel):
    work_orders: list[WorkOrderResponse]


class WorkOrderUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=150)
    issue_description: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, pattern=WORK_ORDER_STATUSES)
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    odometer_at_service: int | None = None
