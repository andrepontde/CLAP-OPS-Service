from datetime import date as EntryDate
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FuelHistoryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: UUID
    date: EntryDate
    odometer: int = Field(ge=0)
    vendor: str = Field(max_length=100)
    fuel_type: str = Field(max_length=50)
    volume: Decimal = Field(gt=0, decimal_places=3)
    total_price: Decimal = Field(ge=0, decimal_places=2)


class FuelHistoryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: UUID | None = None
    date: EntryDate | None = None
    odometer: int | None = Field(default=None, ge=0)
    vendor: str | None = Field(default=None, max_length=100)
    fuel_type: str | None = Field(default=None, max_length=50)
    volume: Decimal | None = Field(default=None, gt=0, decimal_places=3)
    total_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)


class FuelHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vehicle_id: UUID
    date: EntryDate
    odometer: int
    vendor: str
    fuel_type: str
    previous_entry_id: UUID | None
    previous_entry_date: EntryDate | None
    volume: Decimal
    fuel_price: Decimal
    total_price: Decimal
    created_at: datetime


class FuelHistoryList(BaseModel):
    entries: list[FuelHistoryResponse]
