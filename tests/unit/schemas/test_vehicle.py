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
    vehicle = VehicleCreate(
        name="Truck 1",
        type="Truck",
        fuel_type="Diesel",
        vin_sn="VIN123",
        license_plate="ABC123",
        year=2024,
        make="Ford",
        model="Transit",
    )

    assert vehicle.status == "ACTIVE"
    assert vehicle.current_odometer == 0
    assert vehicle.insurance_policy_number is None
    assert vehicle.insurance_expiration is None
    assert vehicle.circulation_card_number is None
    assert vehicle.verification_expiration is None


def test_vehicle_create_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            name="Truck 1",
            type="Truck",
            fuel_type="Diesel",
            vin_sn="VIN123",
            license_plate="ABC123",
            year=2024,
            make="Ford",
            model="Transit",
            status="RETIRED",
        )


def test_vehicle_create_accepts_electric_without_fuel_type() -> None:
    vehicle = VehicleCreate(
        name="Car 1",
        type="Car",
        propulsion_type="ELECTRIC",
        fuel_type=None,
        vin_sn="VIN456",
        license_plate="XYZ123",
        year=2024,
        make="Nissan",
        model="Leaf",
    )

    assert vehicle.propulsion_type == "ELECTRIC"
    assert vehicle.fuel_type is None


@pytest.mark.parametrize("propulsion_type", ["FUEL", "HYBRID"])
def test_vehicle_create_requires_fuel_type(propulsion_type: str) -> None:
    with pytest.raises(ValidationError, match="fuel type is required"):
        VehicleCreate(
            name="Vehicle 1",
            type="Vehicle",
            propulsion_type=propulsion_type,
            fuel_type=None,
            vin_sn="VIN789",
            license_plate="ABC789",
            year=2024,
            make="Example",
            model="Model",
        )


def test_vehicle_create_rejects_fuel_type_for_electric() -> None:
    with pytest.raises(ValidationError, match="fuel type must be null"):
        VehicleCreate(
            name="Car 1",
            type="Car",
            propulsion_type="ELECTRIC",
            fuel_type="Petrol",
            vin_sn="VIN456",
            license_plate="XYZ123",
            year=2024,
            make="Nissan",
            model="Leaf",
        )


def test_vehicle_create_rejects_empty_fuel_type() -> None:
    with pytest.raises(ValidationError):
        VehicleCreate(
            name="Truck 1",
            type="Truck",
            propulsion_type="FUEL",
            fuel_type="",
            vin_sn="VIN456",
            license_plate="XYZ123",
            year=2024,
            make="Ford",
            model="Transit",
        )


def test_vehicle_update_is_partial() -> None:
    update = VehicleUpdate(status="IN_MAINTENANCE")

    assert update.model_dump(exclude_unset=True) == {"status": "IN_MAINTENANCE"}


@pytest.mark.parametrize("field", ["name", "status"])
def test_vehicle_update_rejects_null_required_fields(field: str) -> None:
    with pytest.raises(ValidationError, match="required fields cannot be null"):
        VehicleUpdate(**{field: None})


def test_vehicle_response_reads_attributes_from_a_model() -> None:
    vehicle_id = uuid4()
    fleet_id = uuid4()
    created_at = datetime.now(timezone.utc)
    response = VehicleResponse.model_validate(
        SimpleNamespace(
            id=vehicle_id,
            fleet_id=fleet_id,
            name="Truck 1",
            type="Truck",
            fuel_type="Diesel",
            vin_sn="VIN123",
            license_plate="ABC123",
            year=2024,
            make="Ford",
            model="Transit",
            status="ACTIVE",
            current_odometer=120,
            insurance_policy_number="POL-123",
            insurance_expiration=created_at.date(),
            circulation_card_number="CARD-123",
            verification_expiration=created_at.date(),
            created_at=created_at,
        )
    )

    assert response.id == vehicle_id
    assert response.fleet_id == fleet_id
    assert response.created_at == created_at
