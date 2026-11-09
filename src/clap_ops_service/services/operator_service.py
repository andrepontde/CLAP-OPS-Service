from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.operator import OperatorCreate, OperatorUpdate
from clap_ops_service.database.models import Operator


class OperatorService:
    def __init__(self, db: Session):
        self.db = db

    def create_operator(self, operator_data: OperatorCreate) -> Operator:
        operator = Operator(
            **operator_data.model_dump(exclude={"created_at"})
        )
        self.db.add(operator)
        try:
            self.db.commit()
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError(
                "Unexpected error occurred while creating operator"
            ) from error
        self.db.refresh(operator)
        return operator

    def get_operator(self, operator_id: UUID) -> Operator:
        operator = self.db.query(Operator).filter(Operator.id == operator_id).first()
        if operator is None:
            raise ValueError("Operator not found")
        return operator

    def list_operators(self) -> list[Operator]:
        return self.db.query(Operator).order_by(Operator.full_name).all()

    def update_operator(
        self, operator_id: UUID, operator_data: OperatorUpdate
    ) -> Operator:
        operator = self.get_operator(operator_id)
        for field, value in operator_data.model_dump(exclude_unset=True).items():
            setattr(operator, field, value)
        try:
            self.db.commit()
            self.db.refresh(operator)
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError(
                "Unexpected error occurred while updating operator"
            ) from error
        return operator

    def delete_operator(self, operator_id: UUID) -> None:
        operator = self.get_operator(operator_id)
        self.db.delete(operator)
        try:
            self.db.commit()
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise RuntimeError(
                "Unexpected error occurred while deleting operator"
            ) from error
