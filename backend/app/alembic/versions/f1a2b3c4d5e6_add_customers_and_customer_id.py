"""Add customers table and customer_id to documents and chat messages

Revision ID: f1a2b3c4d5e6
Revises: d4a1b2c3e4f5
Create Date: 2026-06-23 12:00:00.000000

"""
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "f1a2b3c4d5e6"
down_revision = "d4a1b2c3e4f5"
branch_labels = None
depends_on = None

DEFAULT_CUSTOMER_ID = str(uuid.uuid4())


def upgrade():
    op.create_table(
        "customer",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    customer_table = sa.table(
        "customer",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("description", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        customer_table,
        [
            {
                "id": DEFAULT_CUSTOMER_ID,
                "name": "Default",
                "description": "Legacy documents and chat messages",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
            }
        ],
    )

    op.add_column(
        "document",
        sa.Column("customer_id", sa.Uuid(), nullable=True),
    )
    op.execute(
        sa.text(
            f"UPDATE document SET customer_id = '{DEFAULT_CUSTOMER_ID}' WHERE customer_id IS NULL"
        )
    )
    op.alter_column("document", "customer_id", nullable=False)
    op.create_index("ix_document_customer_id", "document", ["customer_id"])
    op.create_foreign_key(
        "document_customer_id_fkey",
        "document",
        "customer",
        ["customer_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.add_column(
        "chatmessage",
        sa.Column("customer_id", sa.Uuid(), nullable=True),
    )
    op.execute(
        sa.text(
            f"UPDATE chatmessage SET customer_id = '{DEFAULT_CUSTOMER_ID}' WHERE customer_id IS NULL"
        )
    )
    op.alter_column("chatmessage", "customer_id", nullable=False)
    op.create_index("ix_chatmessage_customer_id", "chatmessage", ["customer_id"])
    op.create_index(
        "ix_chatmessage_user_id_customer_id",
        "chatmessage",
        ["user_id", "customer_id"],
    )
    op.create_foreign_key(
        "chatmessage_customer_id_fkey",
        "chatmessage",
        "customer",
        ["customer_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint("chatmessage_customer_id_fkey", "chatmessage", type_="foreignkey")
    op.drop_index("ix_chatmessage_user_id_customer_id", table_name="chatmessage")
    op.drop_index("ix_chatmessage_customer_id", table_name="chatmessage")
    op.drop_column("chatmessage", "customer_id")

    op.drop_constraint("document_customer_id_fkey", "document", type_="foreignkey")
    op.drop_index("ix_document_customer_id", table_name="document")
    op.drop_column("document", "customer_id")

    op.drop_table("customer")
