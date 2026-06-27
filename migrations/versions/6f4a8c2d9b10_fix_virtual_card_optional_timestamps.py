"""fix_virtual_card_optional_timestamps

Revision ID: 6f4a8c2d9b10
Revises: 2db51d3b74ae
Create Date: 2026-06-27 18:45:00.000000

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6f4a8c2d9b10"
down_revision: Union[str, None] = "2db51d3b74ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "virtualcard",
        "last_top_up_date",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )
    op.alter_column(
        "virtualcard",
        "blocked_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "virtualcard",
        "blocked_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "virtualcard",
        "last_top_up_date",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
