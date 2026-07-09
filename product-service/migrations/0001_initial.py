"""
Initial migration: create categories and products tables and seed with sample data.
This file is informational; the service uses SQLAlchemy's create_all() and a seeder
(`core/seed.py`) on startup to apply schema and seed data automatically.

If you prefer alembic, generate a real migration using alembic revision --autogenerate.
"""

# Migration: 0001_initial
# - Creates tables via SQLAlchemy models
# - Seeds 2 categories and 5 sample products


def upgrade():
    pass


def downgrade():
    pass
