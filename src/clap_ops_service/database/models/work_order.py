from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..connection import Base


class WorkOrder(Base):
    __tablename__ = "work_orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name="ck_work_orders_status",
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
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    issue_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        default="OPEN",
        server_default="OPEN",
    )
    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scheduled_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    actual_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    actual_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    odometer_at_service: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.clock_timestamp()
    )
