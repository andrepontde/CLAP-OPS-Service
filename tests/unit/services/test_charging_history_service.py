from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest

from clap_ops_service.api.v1.schemas.charging_history import ChargingHistoryCreate
from clap_ops_service.database.models import ChargingHistory, Vehicle
from clap_ops_service.services.charging_history_service import ChargingHistoryService
from clap_ops_service.services.exceptions import ConflictError


FLEET_ID = uuid4()
VEHICLE_ID = uuid4()


def create_data() -> ChargingHistoryCreate:
    started = datetime(2026, 11, 21, 14, 0, tzinfo=timezone.utc)
    return ChargingHistoryCreate(
        vehicle_id=VEHICLE_ID,
        vendor="Charge Station",
        charging_started_at=started,
        charging_ended_at=started + timedelta(minutes=90),
        odometer=1200,
        total_energy_kwh=Decimal("40.000"),
        energy_price=Decimal("0.3000"),
    )


def test_add_charging_entry_calculates_values_and_updates_vehicle(
    db_session: Mock,
) -> None:
    vehicle = Vehicle(
        id=VEHICLE_ID,
        fleet_id=FLEET_ID,
        propulsion_type="ELECTRIC",
        current_odometer=1000,
    )
    previous = ChargingHistory(
        id=uuid4(),
        vehicle_id=VEHICLE_ID,
        charging_started_at=datetime(
            2026,
            11,
20,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )
    vehicle_query = Mock()
    vehicle_query.filter.return_value.first.return_value = vehicle
    previous_query = Mock()
    previous_query.filter.return_value.order_by.return_value.first.return_value = previous
    entries_query = Mock()
    entries_query.filter.return_value.order_by.return_value.all.return_value = [previous]
    db_session.query.side_effect = [vehicle_query, entries_query]

    result = ChargingHistoryService(db_session).add_charging_entry(
        FLEET_ID,
        create_data(),
        "Fleet Admin",
        uuid4(),
    )

    assert result.charging_duration_minutes == 90
    assert result.energy_cost == Decimal("12.00")
    assert result.total_cost == Decimal("12.00")
    assert result.created_by_name == "Fleet Admin"
    assert vehicle.current_odometer == 1200
    db_session.commit.assert_called_once_with()


def test_add_charging_entry_rejects_fuel_vehicle(db_session: Mock) -> None:
    vehicle = Vehicle(
        id=VEHICLE_ID,
        fleet_id=FLEET_ID,
        propulsion_type="FUEL",
        current_odometer=1000,
    )
    vehicle_query = Mock()
    vehicle_query.filter.return_value.first.return_value = vehicle
    db_session.query.return_value = vehicle_query

    with pytest.raises(ConflictError, match="electric or hybrid"):
        ChargingHistoryService(db_session).add_charging_entry(
            FLEET_ID,
            create_data(),
            "Fleet Admin",
            uuid4(),
        )


def test_add_charging_entry_accepts_historical_odometer(db_session: Mock) -> None:
    vehicle = Vehicle(
        id=VEHICLE_ID,
        fleet_id=FLEET_ID,
        propulsion_type="ELECTRIC",
        current_odometer=1000,
    )
    vehicle_query = Mock()
    vehicle_query.filter.return_value.first.return_value = vehicle
    entries_query = Mock()
    entries_query.filter.return_value.order_by.return_value.all.return_value = []
    db_session.query.side_effect = [vehicle_query, entries_query]
    data = create_data()
    data.odometer = 900

    result = ChargingHistoryService(db_session).add_charging_entry(
        FLEET_ID,
        data,
        "Fleet Admin",
        uuid4(),
    )

    assert result.odometer == 900
    assert vehicle.current_odometer == 1000


def test_add_charging_entry_rejects_end_before_start(db_session: Mock) -> None:
    vehicle = Vehicle(
        id=VEHICLE_ID,
        fleet_id=FLEET_ID,
        propulsion_type="HYBRID",
        current_odometer=1000,
    )
    vehicle_query = Mock()
    vehicle_query.filter.return_value.first.return_value = vehicle
    db_session.query.return_value = vehicle_query
    data = create_data()
    data.charging_ended_at = data.charging_started_at - timedelta(minutes=1)

    with pytest.raises(ConflictError, match="at or after"):
        ChargingHistoryService(db_session).add_charging_entry(
            FLEET_ID,
            data,
            "Fleet Admin",
            uuid4(),
        )


def test_rebuild_previous_entries_links_entries_in_start_order(
    db_session: Mock,
) -> None:
    first_start = datetime(2026, 11, 20, 14, 0, tzinfo=timezone.utc)
    second_start = datetime(2026, 11, 21, 14, 0, tzinfo=timezone.utc)
    first = ChargingHistory(
        id=uuid4(),
        charging_started_at=first_start,
    )
    second = ChargingHistory(
        id=uuid4(),
        charging_started_at=second_start,
    )
    entries_query = Mock()
    entries_query.filter.return_value.order_by.return_value.all.return_value = [
        first,
        second,
    ]
    db_session.query.return_value = entries_query

    ChargingHistoryService(db_session)._rebuild_previous_entries(VEHICLE_ID)

    assert first.previous_entry_id is None
    assert first.previous_entry_date is None
    assert second.previous_entry_id == first.id
    assert second.previous_entry_date == first_start
