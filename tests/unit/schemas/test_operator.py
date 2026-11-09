from datetime import datetime, timezone
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


def test_operator_create_uses_active_as_the_default() -> None:
    operator = OperatorCreate(
        full_name="Octavio",
        base_rate_per_trip=Decimal("650.00"),
    )

    assert operator.is_active is True
    assert operator.phone_number is None
    assert operator.email is None


def test_operator_create_accepts_nullable_contact_fields() -> None:
    operator = OperatorCreate(
        full_name="Miguel",
        phone_number="+5215550101234",
        email="miguel@example.com",
        base_rate_per_trip=Decimal("600.00"),
    )

    assert operator.email == "miguel@example.com"
    assert operator.phone_number == "+5215550101234"


def test_operator_create_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        OperatorCreate(
            full_name="Juan Carlos",
            email="not-an-email",
            base_rate_per_trip=Decimal("600.00"),
        )


def test_operator_update_is_partial() -> None:
    update = OperatorUpdate(is_active=False)

    assert update.model_dump(exclude_unset=True) == {"is_active": False}


def test_operator_response_reads_attributes_from_a_model() -> None:
    operator_id = uuid4()
    created_at = datetime.now(timezone.utc)
    response = OperatorResponse.model_validate(
        SimpleNamespace(
            id=operator_id,
            full_name="Octavio",
            phone_number=None,
            email=None,
            base_rate_per_trip=Decimal("650.00"),
            is_active=True,
            created_at=created_at,
        )
    )

    assert response.id == operator_id
    assert response.base_rate_per_trip == Decimal("650.00")
    assert response.created_at == created_at
