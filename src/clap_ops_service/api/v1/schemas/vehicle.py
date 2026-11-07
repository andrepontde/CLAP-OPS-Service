from datetime import date, datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    internal_id: str
    make: str
    model: str
    year: int
    status: str = Field(
        default="ACTIVE", pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$"
    )
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

    internal_id: str | None = None
    make: str | None = None
    model: str | None = None
    year: int | None = None
    status: str | None = Field(
        default=None, pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$"
    )
    current_odometer: int | None = None
    insurance_policy_number: str | None = None
    insurance_expiration: date | None = None
    circulation_card_number: str | None = None
    verification_expiration: date | None = None


class VehicleDelete(BaseModel):
    internal_id: str


class VehicleStatusUpdate(BaseModel):
    status: str = Field(pattern="^(ACTIVE|IN_MAINTENANCE|DECOMMISSIONED)$")