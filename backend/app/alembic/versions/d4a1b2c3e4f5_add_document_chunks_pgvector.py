"""Add document chunks with pgvector embeddings

Revision ID: d4a1b2c3e4f5
Revises: c3d8f1a24b07
Create Date: 2026-06-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "d4a1b2c3e4f5"
down_revision = "c3d8f1a24b07"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "documentchunk",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_type", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["document.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_documentchunk_document_id"),
        "documentchunk",
        ["document_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_documentchunk_document_id"), table_name="documentchunk")
    op.drop_table("documentchunk")
