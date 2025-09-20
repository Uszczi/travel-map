"""halo

Revision ID: 6d7f0917ca7c
Revises: e7c8d2e1abb7
Create Date: 2025-09-20 17:44:19.056640

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6d7f0917ca7c"
down_revision: Union[str, Sequence[str], None] = "e7c8d2e1abb7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "usermodel",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP(0)"),
    )
    op.alter_column(
        "usermodel",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP(0)"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "usermodel",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP(0)"),
    )
    op.alter_column(
        "usermodel",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP(0)"),
    )
