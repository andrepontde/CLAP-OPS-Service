from datetime import date
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from clap_ops_service.api.v1.schemas.operator import OperatorCreate, OperatorUpdate
from clap_ops_service.database.models import Operator
from clap_ops_service.services.exceptions import (
    ConflictError,
    DatabaseOperationError,
    NotFoundError,
)
from clap_ops_service.services.operator_service import OperatorService


def operator_create() -> OperatorCreate:
    return OperatorCreate(
        name="Octavio",
        last_name="Gomez",
        labor_rate=Decimal("650.00"),
        is_operator=True,
        license_expiration_date=date(2027, 1, 1),
    )


def test_create_operator_adds_commits_refreshes_and_returns_operator(
    db_session: Mock,
) -> None:
    result = OperatorService(db_session).create_operator(operator_create())

    assert isinstance(result, Operator)
    assert result.name == "Octavio"
    db_session.add.assert_called_once_with(result)
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(result)


def test_create_operator_reports_duplicate_employee_code(db_session: Mock) -> None:
    db_session.commit.side_effect = IntegrityError(
        "insert operator", {}, UniqueViolation("duplicate employee_code")
    )

    with pytest.raises(ConflictError, match="employee_code already exists"):
        OperatorService(db_session).create_operator(operator_create())

    db_session.rollback.assert_called_once_with()


def test_create_operator_reports_unexpected_database_error(db_session: Mock) -> None:
    db_session.commit.side_effect = SQLAlchemyError("database unavailable")

    with pytest.raises(DatabaseOperationError, match="Could not create operator"):
        OperatorService(db_session).create_operator(operator_create())

    db_session.rollback.assert_called_once_with()


def test_update_operator_changes_only_supplied_fields(db_session: Mock) -> None:
    operator_id = uuid4()
    operator = Operator(
        id=operator_id,
        **operator_create().model_dump(exclude={"created_at"}),
    )
    db_session.query.return_value.filter.return_value.first.return_value = operator

    result = OperatorService(db_session).update_operator(
        operator_id, OperatorUpdate(name="Updated name")
    )

    assert result.name == "Updated name"
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(operator)


def test_get_operator_raises_when_missing(db_session: Mock) -> None:
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(NotFoundError, match="Operator not found"):
        OperatorService(db_session).get_operator(uuid4())


def test_delete_operator_deletes_and_commits(db_session: Mock) -> None:
    operator = Operator(
        id=uuid4(),
        **operator_create().model_dump(exclude={"created_at"}),
    )
    db_session.query.return_value.filter.return_value.first.return_value = operator

    OperatorService(db_session).delete_operator(operator.id)

    db_session.delete.assert_called_once_with(operator)
    db_session.commit.assert_called_once_with()
