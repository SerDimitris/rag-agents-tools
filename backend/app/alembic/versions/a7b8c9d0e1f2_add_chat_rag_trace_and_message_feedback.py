"""Add chat message RAG trace and message feedback

Revision ID: a7b8c9d0e1f2
Revises: f1a2b3c4d5e6
Create Date: 2026-06-25 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "a7b8c9d0e1f2"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None

feedback_rating_enum = postgresql.ENUM(
    "positive",
    "negative",
    name="feedbackrating",
    create_type=False,
)

feedback_reason_enum = postgresql.ENUM(
    "wrong",
    "incomplete",
    "outdated",
    "off_topic",
    "other",
    name="feedbackreason",
    create_type=False,
)


def upgrade():
    op.add_column(
        "chatmessage",
        sa.Column("reply_to_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "chatmessage",
        sa.Column("rag_trace", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_index(
        op.f("ix_chatmessage_reply_to_id"),
        "chatmessage",
        ["reply_to_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_chatmessage_reply_to_id_chatmessage",
        "chatmessage",
        "chatmessage",
        ["reply_to_id"],
        ["id"],
    )

    feedback_rating_enum.create(op.get_bind(), checkfirst=True)
    feedback_reason_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "messagefeedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", feedback_rating_enum, nullable=False),
        sa.Column("reason", feedback_reason_enum, nullable=True),
        sa.Column("comment", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["message_id"], ["chatmessage.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id", "user_id", name="uq_messagefeedback_message_user"),
    )
    op.create_index(
        op.f("ix_messagefeedback_message_id"),
        "messagefeedback",
        ["message_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_messagefeedback_message_id"), table_name="messagefeedback")
    op.drop_table("messagefeedback")
    feedback_reason_enum.drop(op.get_bind(), checkfirst=True)
    feedback_rating_enum.drop(op.get_bind(), checkfirst=True)

    op.drop_constraint(
        "fk_chatmessage_reply_to_id_chatmessage",
        "chatmessage",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_chatmessage_reply_to_id"), table_name="chatmessage")
    op.drop_column("chatmessage", "rag_trace")
    op.drop_column("chatmessage", "reply_to_id")
