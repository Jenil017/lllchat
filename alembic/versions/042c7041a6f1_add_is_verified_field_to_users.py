"""Add is_verified field to users

Revision ID: 042c7041a6f1
Revises: 001_initial
Create Date: 2026-02-05 18:50:09.200939

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "042c7041a6f1"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_verified column to users table
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    # Remove is_verified column from users table
    op.drop_column("users", "is_verified")
