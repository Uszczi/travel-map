"""init migrations

Revision ID: e7c8d2e1abb7
Revises:
Create Date: 2025-09-19 16:01:18.526892

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7c8d2e1abb7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "usermodel",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("current_timestamp(0)"),
            nullable=False,
        ),
        sa.Column(
            "uuid",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("email", sqlmodel.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("uuid"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("usermodel")
