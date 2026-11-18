from uuid import UUID

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from clap_ops_service.api.v1.schemas.operator import OperatorCreate, OperatorUpdate
from clap_ops_service.database.models import Operator
from clap_ops_service.services.exceptions import (
    ConflictError,
    DatabaseOperationError,
    NotFoundError,
)


class OperatorService:
    def __init__(self, db: Session):
        self.db = db

    def create_operator(self, operator_data: OperatorCreate) -> Operator:
        operator = Operator(**operator_data.model_dump(exclude={"created_at"}))
        self.db.add(operator)
        try:
            self.db.commit()
        except IntegrityError as error:
            self.db.rollback()
            if isinstance(error.orig, UniqueViolation):
                raise ConflictError(
                    "An operator with this employee_code already exists"
                ) from error
            raise DatabaseOperationError(
                "Could not create operator"
            ) from error
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise DatabaseOperationError(
                "Could not create operator"
            ) from error
        try:
            self.db.refresh(operator)
        except (SQLAlchemyError, OSError) as error:
            raise DatabaseOperationError(
                "Could not create operator"
            ) from error
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
        try:
            self.db.commit()
            self.db.refresh(operator)
        except IntegrityError as error:
            self.db.rollback()
            if isinstance(error.orig, UniqueViolation):
                raise ConflictError(
                    "An operator with this employee_code already exists"
                ) from error
            raise DatabaseOperationError(
                "Could not update operator"
            ) from error
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise DatabaseOperationError(
                "Could not update operator"
            ) from error
        return operator

    def delete_operator(self, operator_id: UUID) -> None:
        operator = self.get_operator(operator_id)
        self.db.delete(operator)
        try:
            self.db.commit()
        except (SQLAlchemyError, OSError) as error:
            self.db.rollback()
            raise DatabaseOperationError(
                "Could not delete operator"
            ) from error
