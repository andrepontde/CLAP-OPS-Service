"""add work orders table

Revision ID: 1f4b7c9a2d6e
Revises: 8d6a1e2c4b7f
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1f4b7c9a2d6e"
down_revision: Union[str, Sequence[str], None] = "8d6a1e2c4b7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "work_orders",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("vehicle_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("issue_description", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=25),
            server_default=sa.text("'OPEN'"),
            nullable=False,
        ),
        sa.Column(
            "scheduled_start",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("odometer_at_service", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("clock_timestamp()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name="ck_work_orders_status",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_work_orders_vehicle_id"),
        "work_orders",
        ["vehicle_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_work_orders_vehicle_id"), table_name="work_orders")
    op.drop_table("work_orders")
