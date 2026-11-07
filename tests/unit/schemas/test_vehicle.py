from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from clap_ops_service.api.v1.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)


def test_vehicle_create_uses_database_defaults() -> None:
    vehicle = VehicleCreate(internal_id="M1", make="Ford", model="Transit", year=2024)

    assert vehicle.status == "ACTIVE"
    assert vehicle.current_odometer == 0
    assert vehicle.created_at is None


def test_vehicle_create_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            internal_id="M1",
            make="Ford",
            model="Transit",
            year=2024,
            status="RETIRED",
        )


def test_vehicle_update_is_partial() -> None:
    update = VehicleUpdate(status="IN_MAINTENANCE")

    assert update.model_dump(exclude_unset=True) == {"status": "IN_MAINTENANCE"}


def test_vehicle_response_reads_attributes_from_a_model() -> None:
    vehicle_id = uuid4()
    created_at = datetime.now(timezone.utc)
    response = VehicleResponse.model_validate(
        SimpleNamespace(
            id=vehicle_id,
            internal_id="M1",
            make="Ford",
            model="Transit",
            year=2024,
            status="ACTIVE",
            current_odometer=0,
            insurance_policy_number=None,
            insurance_expiration=None,
            circulation_card_number=None,
            verification_expiration=None,
            created_at=created_at,
        )
    )

    assert response.id == vehicle_id
    assert response.created_at == created_at
