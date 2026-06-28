"""fix_ml_model_status_archived_enum

Revision ID: 1c7c3b6ab9d2
Revises: 87a33ff87998
Create Date: 2026-06-29 02:28:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1c7c3b6ab9d2"
down_revision: Union[str, None] = "87a33ff87998"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_enum e
                JOIN pg_type t ON t.oid = e.enumtypid
                WHERE t.typname = 'modelstatusenum'
                  AND e.enumlabel = 'ARCHIVEd'
            )
            AND NOT EXISTS (
                SELECT 1
                FROM pg_enum e
                JOIN pg_type t ON t.oid = e.enumtypid
                WHERE t.typname = 'modelstatusenum'
                  AND e.enumlabel = 'ARCHIVED'
            )
            THEN
                ALTER TYPE modelstatusenum RENAME VALUE 'ARCHIVEd' TO 'ARCHIVED';
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_enum e
                JOIN pg_type t ON t.oid = e.enumtypid
                WHERE t.typname = 'modelstatusenum'
                  AND e.enumlabel = 'ARCHIVED'
            )
            AND NOT EXISTS (
                SELECT 1
                FROM pg_enum e
                JOIN pg_type t ON t.oid = e.enumtypid
                WHERE t.typname = 'modelstatusenum'
                  AND e.enumlabel = 'ARCHIVEd'
            )
            THEN
                ALTER TYPE modelstatusenum RENAME VALUE 'ARCHIVED' TO 'ARCHIVEd';
            END IF;
        END $$;
        """
    )
