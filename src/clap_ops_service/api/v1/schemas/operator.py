from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class OperatorBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        pattern=r"^\+?[1-9]\d{7,14}$",
        max_length=20,
    )
    date_of_birth: date | None = None
    address: str | None = Field(default=None, max_length=255)
    employee_code: str | None = Field(default=None, max_length=6)
    labor_rate: Decimal = Field(
        max_digits=10, decimal_places=2, ge=0
    )
    license_class: str | None = Field(default=None, max_length=50)
    license_expiration_date: date


class OperatorCreate(OperatorBase):
    pass


class OperatorResponse(OperatorBase):
    id: UUID
    created_at: datetime


class OperatorList(BaseModel):
    operators: list[OperatorResponse]


class OperatorUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        pattern=r"^\+?[1-9]\d{7,14}$",
        max_length=20,
    )
    date_of_birth: date | None = None
    address: str | None = Field(default=None, max_length=255)
    employee_code: str | None = Field(default=None, max_length=6)
    labor_rate: Decimal | None = Field(
        default=None, max_digits=10, decimal_places=2, ge=0
    )
    license_class: str | None = Field(default=None, max_length=50)
    license_expiration_date: date | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> "OperatorUpdate":
        required_fields = {"name", "last_name", "labor_rate", "license_expiration_date"}
        if any(
            field in self.model_fields_set and getattr(self, field) is None
            for field in required_fields
        ):
            raise ValueError("required fields cannot be null")
        return self
