from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OperatorBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str = Field(min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    base_rate_per_trip: Decimal = Field(max_digits=10, decimal_places=2)
    is_active: bool = True
    created_at: datetime | None = None


class OperatorCreate(OperatorBase):
    pass


class OperatorResponse(OperatorBase):
    id: UUID


class OperatorList(BaseModel):
    operators: list[OperatorResponse]


class OperatorUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    base_rate_per_trip: Decimal | None = Field(
        default=None, max_digits=10, decimal_places=2
    )
    is_active: bool | None = None
