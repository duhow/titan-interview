"""Create the user table.

Revision ID: 0001_create_user_table
Revises:
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0001_create_user_table"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the application user table."""
    op.create_table(
        "user",
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("birthdate", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("username"),
    )


def downgrade() -> None:
    """Drop the application user table."""
    op.drop_table("user")
