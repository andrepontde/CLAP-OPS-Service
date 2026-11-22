from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from clap_ops_service.api.v1.schemas.charging_history import ChargingHistoryCreate


def test_charging_history_create_accepts_required_fields() -> None:
    started = datetime(2026, 11, 21, 14, 0, tzinfo=timezone.utc)
    entry = ChargingHistoryCreate(
        vehicle_id=uuid4(),
        vendor="Charge Station",
        charging_started_at=started,
        charging_ended_at=started + timedelta(minutes=90),
        odometer=1200,
        total_energy_kwh=Decimal("40.000"),
        energy_price=Decimal("0.3000"),
    )



def test_charging_history_rejects_end_before_start() -> None:
    started = datetime(2026, 11, 21, 14, 0, tzinfo=timezone.utc)

    with pytest.raises(ValidationError, match="charging end"):
        ChargingHistoryCreate(
            vehicle_id=uuid4(),
            vendor="Charge Station",
            charging_started_at=started,
            charging_ended_at=started - timedelta(minutes=1),
            odometer=1200,
            total_energy_kwh=Decimal("40.000"),
            energy_price=Decimal("0.3000"),
        )


def test_charging_history_rejects_odometer_out_of_range() -> None:
    started = datetime(2026, 11, 21, 14, 0, tzinfo=timezone.utc)

    with pytest.raises(ValidationError):
        ChargingHistoryCreate(
            vehicle_id=uuid4(),
            vendor="Charge Station",
            charging_started_at=started,
            charging_ended_at=started + timedelta(minutes=90),
            odometer=23_123_123_123,
            total_energy_kwh=Decimal("40.000"),
            energy_price=Decimal("0.3000"),
        )
