from datetime import date, datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(max_length=100)
    status: str = Field(
        default="ACTIVE", pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$"
    )
    type: str = Field(max_length=50)
    fuel_type: str = Field(max_length=50)
    vin_sn: str = Field(max_length=100)
    license_plate: str = Field(max_length=20)
    year: int = Field(ge=1886, le=2100)
    make: str = Field(max_length=50)
    model: str = Field(max_length=50)
    current_odometer: int = Field(default=0, ge=0)
    insurance_policy_number: str | None = Field(default=None, max_length=100)
    insurance_expiration: date | None = None
    circulation_card_number: str | None = Field(default=None, max_length=100)
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

    name: str | None = Field(default=None, max_length=100)
    status: str | None = Field(
        default=None, pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$"
    )
    type: str | None = Field(default=None, max_length=50)
    fuel_type: str | None = Field(default=None, max_length=50)
    vin_sn: str | None = Field(default=None, max_length=100)
    license_plate: str | None = Field(default=None, max_length=20)
    year: int | None = Field(default=None, ge=1886, le=2100)
    make: str | None = Field(default=None, max_length=50)
    model: str | None = Field(default=None, max_length=50)
    current_odometer: int | None = Field(default=None, ge=0)
    insurance_policy_number: str | None = Field(default=None, max_length=100)
    insurance_expiration: date | None = None
    circulation_card_number: str | None = Field(default=None, max_length=100)
    verification_expiration: date | None = None


class VehicleStatusUpdate(BaseModel):
    status: str = Field(pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$")