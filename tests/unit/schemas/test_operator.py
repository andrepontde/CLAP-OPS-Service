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


def test_operator_create_requires_license_expiration() -> None:
    with pytest.raises(ValidationError, match="license_expiration_date"):
        OperatorCreate(
            name="Octavio",
            last_name="Gomez",
            labor_rate=Decimal("650.00"),
        )


def test_operator_create_accepts_license_expiration() -> None:
    operator = OperatorCreate(
        name="Octavio",
        last_name="Gomez",
        labor_rate=Decimal("650.00"),
        license_expiration_date=date(2027, 1, 1),
    )

    assert operator.license_expiration_date == date(2027, 1, 1)
    assert operator.email is None


def test_operator_create_accepts_nullable_contact_fields() -> None:
    operator = OperatorCreate(
        name="Miguel",
        last_name="Lopez",
        phone="+5215550101234",
        email="miguel@example.com",
        labor_rate=Decimal("600.00"),
        license_expiration_date=date(2027, 1, 1),
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
            license_expiration_date=date(2027, 1, 1),
        )


def test_operator_create_rejects_invalid_phone() -> None:
    with pytest.raises(ValidationError):
        OperatorCreate(
            name="Juan",
            last_name="Carlos",
            phone="555-010-1234",
            labor_rate=Decimal("600.00"),
            license_expiration_date=date(2027, 1, 1),
        )


def test_operator_update_rejects_null_license_expiration() -> None:
    with pytest.raises(ValidationError, match="license_expiration_date"):
        OperatorUpdate(license_expiration_date=None)


@pytest.mark.parametrize("field", ["name", "labor_rate"])
def test_operator_update_rejects_null_required_fields(field: str) -> None:
    with pytest.raises(ValidationError, match="required fields cannot be null"):
        OperatorUpdate(**{field: None})


def test_operator_update_is_partial() -> None:
    update = OperatorUpdate(name="Updated name")

    assert update.model_dump(exclude_unset=True) == {"name": "Updated name"}


def test_operator_response_reads_attributes_from_a_model() -> None:
    operator_id = uuid4()
    created_at = datetime.now(timezone.utc)
    response = OperatorResponse.model_validate(
        SimpleNamespace(
            id=operator_id,
            name="Octavio",
            last_name="Gomez",
            email=None,
            phone="+15550101234",
            date_of_birth=date(1990, 1, 1),
            address=None,
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
