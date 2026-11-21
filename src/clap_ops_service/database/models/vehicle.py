from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..connection import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint("fleet_id", "name", name="uq_vehicles_fleet_name"),
        UniqueConstraint("fleet_id", "vin_sn", name="uq_vehicles_fleet_vin"),
        CheckConstraint(
            "propulsion_type IN ('FUEL', 'ELECTRIC', 'HYBRID')",
            name="ck_vehicles_propulsion_type",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'IN_MAINTENANCE', 'DECOMMISSIONED')",
            name="ck_vehicles_status",
        ),
        CheckConstraint(
            "current_odometer >= 0",
            name="ck_vehicles_current_odometer_non_negative",
        ),
        CheckConstraint(
            "year BETWEEN 1886 AND 2100",
            name="ck_vehicles_year_range",
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
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        default="ACTIVE",
        server_default="ACTIVE",
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    propulsion_type: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        default="FUEL",
        server_default="FUEL",
    )
    fuel_type: Mapped[Optional[str]] = mapped_column(String(50))
    vin_sn: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    license_plate: Mapped[str] = mapped_column(String(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    make: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
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