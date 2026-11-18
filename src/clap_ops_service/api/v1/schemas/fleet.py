from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FleetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class FleetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    created_at: datetime


class FleetList(BaseModel):
    fleets: list[FleetResponse]


class FleetMembershipCreate(BaseModel):
    role: str = Field(pattern="^(MANAGER|MEMBER)$")
