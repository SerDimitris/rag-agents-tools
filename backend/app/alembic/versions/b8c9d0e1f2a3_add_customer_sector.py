"""Add customer sector for chat prompt profiles

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-06-26 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "b8c9d0e1f2a3"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None

customer_sector_enum = postgresql.ENUM(
    "banking",
    "telecom",
    "energy",
    "general",
    name="customersector",
    create_type=False,
)


def upgrade():
    customer_sector_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "customer",
        sa.Column(
            "sector",
            customer_sector_enum,
            nullable=False,
            server_default="general",
        ),
    )
    op.alter_column("customer", "sector", server_default=None)


def downgrade():
    op.drop_column("customer", "sector")
    customer_sector_enum.drop(op.get_bind(), checkfirst=True)
