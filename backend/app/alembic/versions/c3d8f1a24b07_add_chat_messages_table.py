"""Add chat messages table

Revision ID: c3d8f1a24b07
Revises: b7c4e2a91f03
Create Date: 2026-06-15 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c3d8f1a24b07"
down_revision = "b7c4e2a91f03"
branch_labels = None
depends_on = None

chat_message_role_enum = postgresql.ENUM(
    "user",
    "assistant",
    name="chatmessagerole",
    create_type=False,
)


def upgrade():
    chat_message_role_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "chatmessage",
        sa.Column("content", sa.String(length=10000), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", chat_message_role_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("chatmessage")
    chat_message_role_enum.drop(op.get_bind(), checkfirst=True)
