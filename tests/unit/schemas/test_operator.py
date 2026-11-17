from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from clap_ops_service.api.v1.schemas.operator import (
    OperatorCreate,
    OperatorResponse,
    OperatorUpdate,
)


def test_operator_create_uses_boolean_defaults() -> None:
    operator = OperatorCreate(
        name="Octavio",
        last_name="Gomez",
        labor_rate=Decimal("650.00"),
    )

    assert operator.is_employee is False
    assert operator.is_operator is False
    assert operator.email is None


def test_operator_create_accepts_nullable_contact_fields() -> None:
    operator = OperatorCreate(
        name="Miguel",
        last_name="Lopez",
        phone="+5215550101234",
        email="miguel@example.com",
        labor_rate=Decimal("600.00"),
    )

    assert operator.email == "miguel@example.com"
    assert operator.phone == "+5215550101234"


def test_operator_create_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        OperatorCreate(
            name="Juan",
            last_name="Carlos",
            email="not-an-email",
            labor_rate=Decimal("600.00"),
        )


def test_operator_create_rejects_invalid_phone() -> None:
    with pytest.raises(ValidationError):
        OperatorCreate(
            name="Juan",
            last_name="Carlos",
            phone="555-010-1234",
            labor_rate=Decimal("600.00"),
        )


def test_operator_requires_license_expiration_when_operator() -> None:
    with pytest.raises(ValidationError, match="license_expiration_date"):
        OperatorCreate(
            name="Juan",
            last_name="Carlos",
            labor_rate=Decimal("600.00"),
            is_operator=True,
        )


def test_operator_update_is_partial() -> None:
    update = OperatorUpdate(is_employee=True)

    assert update.model_dump(exclude_unset=True) == {"is_employee": True}


def test_operator_response_reads_attributes_from_a_model() -> None:
    operator_id = uuid4()
    created_at = datetime.now(timezone.utc)
    response = OperatorResponse.model_validate(
        SimpleNamespace(
            id=operator_id,
            name="Octavio",
            last_name="Gomez",
            email=None,
            phone="555-010-1234",
            date_of_birth=date(1990, 1, 1),
            address=None,
            is_employee=True,
            is_operator=True,
            employee_code="EMP001",
            labor_rate=Decimal("650.00"),
            license_class="B",
            license_expiration_date=date(2027, 1, 1),
            created_at=created_at,
        )
    )

    assert response.id == operator_id
    assert response.labor_rate == Decimal("650.00")
    assert response.created_at == created_at
