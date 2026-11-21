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
    entries_query = Mock()
    entries_query.filter.return_value.order_by.return_value.all.return_value = [previous]
    db_session.query.side_effect = [vehicle_query, entries_query]

    result = FuelHistoryService(db_session).add_fuel_entry(
        FLEET_ID,
        create_data(),
        "Fleet Admin",
    )

    assert result.fuel_price == Decimal("1.5000")
    assert result.created_by_name == "Fleet Admin"
    assert vehicle.current_odometer == 1200
    db_session.commit.assert_called_once_with()
    db_session.refresh.assert_called_once_with(result)


def test_create_rejects_lower_odometer(db_session: Mock) -> None:
    vehicle = Vehicle(id=VEHICLE_ID, fleet_id=FLEET_ID, current_odometer=1000)
    vehicle_query = Mock()
    vehicle_query.filter.return_value.first.return_value = vehicle
    entries_query = Mock()
    entries_query.filter.return_value.order_by.return_value.all.return_value = []
    db_session.query.side_effect = [vehicle_query, entries_query]

    result = FuelHistoryService(db_session).add_fuel_entry(
        FLEET_ID,
        create_data(odometer=900),
        "Fleet Admin",
    )

    assert result.odometer == 900
    assert vehicle.current_odometer == 1000


def test_create_rejects_electric_vehicle(db_session: Mock) -> None:
    vehicle = Vehicle(
        id=VEHICLE_ID,
        fleet_id=FLEET_ID,
        propulsion_type="ELECTRIC",
        current_odometer=1000,
    )
    vehicle_query = Mock()
    vehicle_query.filter.return_value.first.return_value = vehicle
    db_session.query.return_value = vehicle_query

    with pytest.raises(ConflictError, match="fuel or hybrid"):
        FuelHistoryService(db_session).add_fuel_entry(
            FLEET_ID,
            create_data(),
            "Fleet Admin",
        )

    db_session.add.assert_not_called()


def test_rebuild_previous_entries_links_entries_in_date_order(
    db_session: Mock,
) -> None:
    first = FuelHistory(id=uuid4(), date=date(2026, 11, 20))
    second = FuelHistory(id=uuid4(), date=date(2026, 11, 21))
    entries_query = Mock()
    entries_query.filter.return_value.order_by.return_value.all.return_value = [
        first,
        second,
    ]
    db_session.query.return_value = entries_query

    FuelHistoryService(db_session)._rebuild_previous_entries(VEHICLE_ID)

    assert first.previous_entry_id is None
    assert first.previous_entry_date is None
    assert second.previous_entry_id == first.id
    assert second.previous_entry_date == first.date
