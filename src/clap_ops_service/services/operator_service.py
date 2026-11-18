from uuid import UUID

from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.operator import OperatorCreate, OperatorUpdate
from clap_ops_service.database.models import Operator
from clap_ops_service.services.database_helpers import database_operation
from clap_ops_service.services.exceptions import (
    NotFoundError,
)


class OperatorService:
    def __init__(self, db: Session):
        self.db = db

    def create_operator(self, operator_data: OperatorCreate) -> Operator:
        operator = Operator(**operator_data.model_dump())
        self.db.add(operator)
        with database_operation(
            self.db,
            "create operator",
            "An operator with this employee_code already exists",
        ):
            self.db.commit()
            self.db.refresh(operator)
        return operator

    def get_operator(self, operator_id: UUID) -> Operator:
        operator = self.db.query(Operator).filter(Operator.id == operator_id).first()
        if operator is None:
            raise NotFoundError("Operator not found")
        return operator

    def list_operators(self) -> list[Operator]:
        return self.db.query(Operator).order_by(Operator.name).all()

    def update_operator(
        self, operator_id: UUID, operator_data: OperatorUpdate
    ) -> Operator:
        operator = self.get_operator(operator_id)
        for field, value in operator_data.model_dump(exclude_unset=True).items():
            setattr(operator, field, value)
        OperatorCreate.model_validate(operator)
        with database_operation(
            self.db,
            "update operator",
            "An operator with this employee_code already exists",
        ):
            self.db.commit()
            self.db.refresh(operator)
        return operator

    def delete_operator(self, operator_id: UUID) -> None:
        operator = self.get_operator(operator_id)
        self.db.delete(operator)
        with database_operation(self.db, "delete operator"):
            self.db.commit()
