from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from clap_ops_service.api.v1.schemas.fuel_history import FuelHistoryCreate


def test_fuel_history_create_accepts_required_fields() -> None:
    entry = FuelHistoryCreate(
        vehicle_id=uuid4(),
        date=date(2026, 11, 21),
        odometer=12345,
        vendor="Fuel Stop",
        fuel_type="Diesel",
        volume=Decimal("50.000"),
        total_price=Decimal("75.00"),
    )

    assert entry.volume == Decimal("50.000")
    assert entry.total_price == Decimal("75.00")


def test_fuel_history_create_rejects_empty_fuel_type() -> None:
    with pytest.raises(ValidationError):
        FuelHistoryCreate(
            vehicle_id=uuid4(),
            date=date(2026, 11, 21),
            odometer=12345,
            vendor="Fuel Stop",
            fuel_type="",
            volume=Decimal("50.000"),
            total_price=Decimal("75.00"),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("odometer", -1),
        ("volume", Decimal("0")),
        ("total_price", Decimal("-1")),
    ],
)
def test_fuel_history_create_rejects_invalid_values(
    field: str,
    value: object,
) -> None:
    values = {
        "vehicle_id": uuid4(),
        "date": date(2026, 11, 21),
        "odometer": 12345,
        "vendor": "Fuel Stop",
        "fuel_type": "Diesel",
        "volume": Decimal("50.000"),
        "total_price": Decimal("75.00"),
    }
    values[field] = value

    with pytest.raises(ValidationError):
        FuelHistoryCreate(**values)
