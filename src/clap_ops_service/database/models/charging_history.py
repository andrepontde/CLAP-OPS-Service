from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..connection import Base


class ChargingHistory(Base):
    __tablename__ = "charging_history"
    __table_args__ = (
        CheckConstraint(
            "odometer >= 0",
            name="ck_charging_history_odometer_non_negative",
        ),
        CheckConstraint(
            "charging_duration_minutes >= 0",
            name="ck_charging_history_duration_non_negative",
        ),
        CheckConstraint(
            "total_energy_kwh > 0",
            name="ck_charging_history_energy_positive",
        ),
        CheckConstraint(
            "energy_price >= 0",
            name="ck_charging_history_energy_price_non_negative",
        ),
        CheckConstraint(
            "energy_cost >= 0",
            name="ck_charging_history_energy_cost_non_negative",
        ),
        CheckConstraint(
            "total_cost >= 0",
            name="ck_charging_history_total_cost_non_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    vehicle_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_name: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor: Mapped[str] = mapped_column(String(100), nullable=False)
    charging_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    charging_ended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    charging_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    odometer: Mapped[int] = mapped_column(Integer, nullable=False)
    total_energy_kwh: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=3),
        nullable=False,
    )
    energy_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=4),
        nullable=False,
    )
    energy_cost: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
    )
    previous_entry_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("charging_history.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    previous_entry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
    )

    previous_entry: Mapped[Optional["ChargingHistory"]] = relationship(
        "ChargingHistory",
        remote_side="ChargingHistory.id",
        foreign_keys=[previous_entry_id],
    )
