#! /usr/bin/env bash

set -e
set -x

# Ensure pgvector is available before migrations/models touch vector columns
python - <<'PY'
from sqlalchemy import create_engine, text

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
with engine.connect() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    connection.commit()
PY

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/initial_data.py
