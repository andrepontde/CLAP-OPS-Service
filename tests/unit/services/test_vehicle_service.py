from unittest.mock import Mock
from datetime import date
from uuid import uuid4

import pytest
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from clap_ops_service.api.v1.schemas.vehicle import VehicleCreate, VehicleUpdate
from clap_ops_service.database.models import Vehicle
from clap_ops_service.services.exceptions import ConflictError, NotFoundError
from clap_ops_service.services.vehicle_service import VehicleService


def vehicle_create() -> VehicleCreate:
    return VehicleCreate(
        name="Truck 1",
        type="Truck",
        fuel_type="Diesel",
        vin_sn="VIN123",
        license_plate="ABC123",
        make="Ford",
        model="Transit",
        year=2024,
    )


def test_create_vehicle_adds_commits_refreshes_and_returns_vehicle(db_session: Mock) -> None:
    result = VehicleService(db_session).create_vehicle(vehicle_create())

    assert isinstance(result, Vehicle)
    assert result.name == "Truck 1"
    db_session.add.assert_called_once_with(result)
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(result)


def test_create_vehicle_reports_duplicate_name(db_session: Mock) -> None:
    db_session.commit.side_effect = IntegrityError(
        "insert vehicle", {}, UniqueViolation("duplicate name")
    )

    with pytest.raises(ConflictError, match="name or VIN already exists"):
        VehicleService(db_session).create_vehicle(vehicle_create())

    db_session.rollback.assert_called_once_with()


def test_update_vehicle_changes_only_supplied_fields(db_session: Mock) -> None:
    vehicle_id = uuid4()
    vehicle = Vehicle(id=vehicle_id, **vehicle_create().model_dump(exclude={"created_at"}))
    db_session.query.return_value.filter.return_value.first.return_value = vehicle

    result = VehicleService(db_session).update_vehicle(
        vehicle_id, VehicleUpdate(name="Truck 2")
    )

    assert result.name == "Truck 2"
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(vehicle)


def test_update_vehicle_changes_vehicle_details(db_session: Mock) -> None:
    vehicle_id = uuid4()
    vehicle = Vehicle(id=vehicle_id, **vehicle_create().model_dump(exclude={"created_at"}))
    db_session.query.return_value.filter.return_value.first.return_value = vehicle

    result = VehicleService(db_session).update_vehicle(
        vehicle_id,
        VehicleUpdate(
            current_odometer=120,
            insurance_policy_number="POL-123",
            insurance_expiration=date(2027, 1, 1),
            circulation_card_number="CARD-123",
            verification_expiration=date(2027, 1, 1),
        ),
    )

    assert result.current_odometer == 120
    assert result.insurance_policy_number == "POL-123"
    assert result.insurance_expiration == date(2027, 1, 1)
    assert result.circulation_card_number == "CARD-123"
    assert result.verification_expiration == date(2027, 1, 1)


def test_get_vehicle_raises_when_missing(db_session: Mock) -> None:
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(NotFoundError, match="Vehicle not found"):
        VehicleService(db_session).get_vehicle(uuid4())


def test_delete_vehicle_deletes_and_commits(db_session: Mock) -> None:
    vehicle = Vehicle(id=uuid4(), **vehicle_create().model_dump(exclude={"created_at"}))
    db_session.query.return_value.filter.return_value.first.return_value = vehicle

    VehicleService(db_session).delete_vehicle(vehicle.id)

    db_session.delete.assert_called_once_with(vehicle)
    db_session.commit.assert_called_once_with()
