from datetime import date, datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    status: str = Field(
        default="ACTIVE", pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$"
    )
    type: str
    fuel_type: str
    vin_sn: str
    license_plate: str
    year: int
    make: str
    model: str
    current_odometer: int = 0
    insurance_policy_number: str | None = None
    insurance_expiration: date | None = None
    circulation_card_number: str | None = None
    verification_expiration: date | None = None
    created_at: datetime | None = None


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: uuid.UUID


class VehicleList(BaseModel):
    vehicles: list[VehicleResponse]


class VehicleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str | None = None
    status: str | None = Field(
        default=None, pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$"
    )
    type: str | None = None
    fuel_type: str | None = None
    vin_sn: str | None = None
    license_plate: str | None = None
    year: int | None = None
    make: str | None = None
    model: str | None = None
    current_odometer: int | None = None
    insurance_policy_number: str | None = None
    insurance_expiration: date | None = None
    circulation_card_number: str | None = None
    verification_expiration: date | None = None


class VehicleDelete(BaseModel):
    name: str


class VehicleStatusUpdate(BaseModel):
    status: str = Field(pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$")