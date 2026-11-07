from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..connection import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'IN_MAINTENANCE', 'DECOMMISSIONED')",
            name="ck_vehicles_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    internal_id: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, index=True
    )
    make: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        default="ACTIVE",
        server_default="ACTIVE",
    )
    current_odometer: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(100))
    insurance_expiration: Mapped[Optional[date]] = mapped_column(Date)
    circulation_card_number: Mapped[Optional[str]] = mapped_column(String(100))
    verification_expiration: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.clock_timestamp()
    )