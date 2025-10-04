"""add is_email_verified

Revision ID: 5aab456798d4
Revises: e2703a29f660
Create Date: 2025-10-04 17:26:45.725604

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "5aab456798d4"
down_revision: Union[str, Sequence[str], None] = "e2703a29f660"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usermodel", sa.Column("is_email_verified", sa.Boolean(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("usermodel", "is_email_verified")
