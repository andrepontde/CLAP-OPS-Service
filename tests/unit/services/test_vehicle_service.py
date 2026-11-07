from unittest.mock import Mock
from uuid import uuid4

import pytest
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from clap_ops_service.api.v1.schemas.vehicle import VehicleCreate, VehicleUpdate
from clap_ops_service.database.models import Vehicle
from clap_ops_service.services.vehicle_service import VehicleService


def vehicle_create() -> VehicleCreate:
    return VehicleCreate(
        internal_id="M1",
        make="Ford",
        model="Transit",
        year=2024,
    )


def test_create_vehicle_adds_commits_refreshes_and_returns_vehicle(db_session: Mock) -> None:
    result = VehicleService(db_session).create_vehicle(vehicle_create())

    assert isinstance(result, Vehicle)
    assert result.internal_id == "M1"
    db_session.add.assert_called_once_with(result)
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(result)


def test_create_vehicle_reports_duplicate_internal_id(db_session: Mock) -> None:
    db_session.commit.side_effect = IntegrityError(
        "insert vehicle", {}, UniqueViolation("duplicate internal_id")
    )

    with pytest.raises(ValueError, match="internal_id already exists"):
        VehicleService(db_session).create_vehicle(vehicle_create())

    db_session.rollback.assert_called_once_with()


def test_update_vehicle_changes_only_supplied_fields(db_session: Mock) -> None:
    vehicle_id = uuid4()
    vehicle = Vehicle(id=vehicle_id, **vehicle_create().model_dump(exclude={"created_at"}))
    db_session.query.return_value.filter.return_value.first.return_value = vehicle

    result = VehicleService(db_session).update_vehicle(
        vehicle_id, VehicleUpdate(current_odometer=120)
    )

    assert result.current_odometer == 120
    assert result.internal_id == "M1"
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(vehicle)


def test_get_vehicle_raises_when_missing(db_session: Mock) -> None:
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(ValueError, match="Vehicle not found"):
        VehicleService(db_session).get_vehicle(uuid4())


def test_delete_vehicle_deletes_and_commits(db_session: Mock) -> None:
    vehicle = Vehicle(id=uuid4(), **vehicle_create().model_dump(exclude={"created_at"}))
    db_session.query.return_value.filter.return_value.first.return_value = vehicle

    VehicleService(db_session).delete_vehicle(vehicle.id)

    db_session.delete.assert_called_once_with(vehicle)
    db_session.commit.assert_called_once_with()
