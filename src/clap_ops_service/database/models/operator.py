from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..connection import Base


class Operator(Base):
    __tablename__ = "operators"
    __table_args__ = (
        UniqueConstraint(
            "fleet_id",
            "employee_code",
            name="uq_operators_fleet_employee_code",
        ),
        CheckConstraint(
            "labor_rate >= 0",
            name="ck_operators_labor_rate_non_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    fleet_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("fleets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(320))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    address: Mapped[Optional[str]] = mapped_column(String(255))
    employee_code: Mapped[Optional[str]] = mapped_column(
        String(6), nullable=True
    )
    labor_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    license_class: Mapped[Optional[str]] = mapped_column(String(50))
    license_expiration_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.clock_timestamp()
    )
