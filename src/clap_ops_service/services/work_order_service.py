from uuid import UUID

from psycopg.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderUpdate,
)
from clap_ops_service.database.models import WorkOrder


class WorkOrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_work_order(self, work_order_data: WorkOrderCreate) -> WorkOrder:
        work_order = WorkOrder(
            **work_order_data.model_dump(exclude={"created_at"})
        )
        self.db.add(work_order)
        try:
            self.db.commit()
        except IntegrityError as error:
            self.db.rollback()
            if isinstance(error.orig, ForeignKeyViolation):
                raise ValueError("Vehicle not found") from error
            raise RuntimeError(
                "Unexpected database integrity error while creating work order"
            ) from error
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError(
                "Unexpected error occurred while creating work order"
            ) from error
        self.db.refresh(work_order)
        return work_order

    def get_work_order(self, work_order_id: UUID) -> WorkOrder:
        work_order = (
            self.db.query(WorkOrder)
            .filter(WorkOrder.id == work_order_id)
            .first()
        )
        if work_order is None:
            raise ValueError("Work order not found")
        return work_order

    def list_work_orders(self) -> list[WorkOrder]:
        return (
            self.db.query(WorkOrder)
            .order_by(WorkOrder.scheduled_start)
            .all()
        )

    def update_work_order(
        self, work_order_id: UUID, work_order_data: WorkOrderUpdate
    ) -> WorkOrder:
        work_order = self.get_work_order(work_order_id)
        for field, value in work_order_data.model_dump(
            exclude_unset=True
        ).items():
            setattr(work_order, field, value)
        try:
            self.db.commit()
            self.db.refresh(work_order)
        except IntegrityError as error:
            self.db.rollback()
            if isinstance(error.orig, ForeignKeyViolation):
                raise ValueError("Vehicle not found") from error
            raise RuntimeError(
                "Unexpected database integrity error while updating work order"
            ) from error
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError(
                "Unexpected error occurred while updating work order"
            ) from error
        return work_order

    def delete_work_order(self, work_order_id: UUID) -> None:
        work_order = self.get_work_order(work_order_id)
        self.db.delete(work_order)
        try:
            self.db.commit()
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError(
                "Unexpected error occurred while deleting work order"
            ) from error
