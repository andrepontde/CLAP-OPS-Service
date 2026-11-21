from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
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


class FuelHistory(Base):
    __tablename__ = "fuel_history"
    __table_args__ = (
        CheckConstraint("odometer >= 0", name="ck_fuel_history_odometer_non_negative"),
        CheckConstraint("volume > 0", name="ck_fuel_history_volume_positive"),
        CheckConstraint("fuel_price >= 0", name="ck_fuel_history_fuel_price_non_negative"),
        CheckConstraint("total_price >= 0", name="ck_fuel_history_total_price_non_negative"),
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
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    odometer: Mapped[int] = mapped_column(Integer, nullable=False)
    vendor: Mapped[str] = mapped_column(String(100), nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_entry_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("fuel_history.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    previous_entry_date: Mapped[Optional[date]] = mapped_column(Date)
    volume: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=3),
        nullable=False,
    )
    fuel_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=4),
        nullable=False,
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.clock_timestamp(),
    )

    previous_entry: Mapped[Optional["FuelHistory"]] = relationship(
        "FuelHistory",
        remote_side="FuelHistory.id",
        foreign_keys=[previous_entry_id],
    )
