from datetime import date
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest

from clap_ops_service.api.v1.schemas.fuel_history import FuelHistoryCreate
from clap_ops_service.database.models import FuelHistory, Vehicle
from clap_ops_service.services.exceptions import ConflictError
from clap_ops_service.services.fuel_history_service import FuelHistoryService


FLEET_ID = uuid4()
VEHICLE_ID = uuid4()


def create_data(odometer: int = 1200) -> FuelHistoryCreate:
    return FuelHistoryCreate(
        vehicle_id=VEHICLE_ID,
        date=date(2026, 11, 21),
        odometer=odometer,
        vendor="Fuel Stop",
        fuel_type="Diesel",
        volume=Decimal("50.000"),
        total_price=Decimal("75.00"),
    )


def test_create_calculates_price_links_previous_and_updates_vehicle(
    db_session: Mock,
) -> None:
    vehicle = Vehicle(id=VEHICLE_ID, fleet_id=FLEET_ID, current_odometer=1000)
    previous = FuelHistory(
        id=uuid4(),
        vehicle_id=VEHICLE_ID,
        date=date(2026, 11, 20),
    )
    vehicle_query = Mock()
    vehicle_query.filter.return_value.first.return_value = vehicle
    previous_query = Mock()
    previous_query.filter.return_value.order_by.return_value.first.return_value = previous
    db_session.query.side_effect = [vehicle_query, previous_query]

    result = FuelHistoryService(db_session).add_fuel_entry(
        FLEET_ID,
        create_data(),
    )

    assert result.fuel_price == Decimal("1.5000")
    assert result.previous_entry_id == previous.id
    assert result.previous_entry_date == previous.date
    assert vehicle.current_odometer == 1200
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(result)


def test_create_rejects_lower_odometer(db_session: Mock) -> None:
    vehicle = Vehicle(id=VEHICLE_ID, fleet_id=FLEET_ID, current_odometer=1000)
    vehicle_query = Mock()
    vehicle_query.filter.return_value.first.return_value = vehicle
    db_session.query.return_value = vehicle_query

    with pytest.raises(ConflictError, match="cannot be lower"):
        FuelHistoryService(db_session).add_fuel_entry(
            FLEET_ID,
            create_data(odometer=900),
        )

    db_session.add.assert_not_called()
    db_session.commit.assert_not_called()
