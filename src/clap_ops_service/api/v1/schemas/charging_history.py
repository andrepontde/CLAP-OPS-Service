from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChargingHistoryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: UUID
    vendor: str = Field(max_length=100)
    charging_started_at: datetime
    charging_ended_at: datetime
    odometer: int = Field(ge=0, le=2_147_483_647)
    total_energy_kwh: Decimal = Field(gt=0, decimal_places=3)
    energy_price: Decimal = Field(ge=0, decimal_places=4)

    @model_validator(mode="after")
    def validate_charging_period(self) -> "ChargingHistoryCreate":
        if self.charging_ended_at < self.charging_started_at:
            raise ValueError("charging end must be at or after charging start")
        return self


class ChargingHistoryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: UUID | None = None
    vendor: str | None = Field(default=None, max_length=100)
    charging_started_at: datetime | None = None
    charging_ended_at: datetime | None = None
    odometer: int | None = Field(default=None, ge=0, le=2_147_483_647)
    total_energy_kwh: Decimal | None = Field(default=None, gt=0, decimal_places=3)
    energy_price: Decimal | None = Field(default=None, ge=0, decimal_places=4)

    @model_validator(mode="after")
    def validate_charging_period(self) -> "ChargingHistoryUpdate":
        if (
            self.charging_started_at is not None
            and self.charging_ended_at is not None
            and self.charging_ended_at < self.charging_started_at
        ):
            raise ValueError("charging end must be at or after charging start")
        return self


class ChargingHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vehicle_id: UUID
    created_by_name: str
    created_by_admin_id: UUID | None
    vendor: str
    charging_started_at: datetime
    charging_ended_at: datetime
    charging_duration_minutes: int
    odometer: int
    total_energy_kwh: Decimal
    energy_price: Decimal
    energy_cost: Decimal
    total_cost: Decimal
    previous_entry_id: UUID | None
    previous_entry_date: datetime | None
    created_at: datetime


class ChargingHistoryList(BaseModel):
    entries: list[ChargingHistoryResponse]
