"""fix_salutation_enum_type

Revision ID: b4d3a6f0c8a1
Revises: 99ba263591ca
Create Date: 2026-06-25 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b4d3a6f0c8a1"
down_revision: Union[str, None] = "99ba263591ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            title_type text;
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'salutationenum'
            ) THEN
                IF EXISTS (
                    SELECT 1
                    FROM pg_type
                    WHERE typname = 'salutaionenum'
                ) THEN
                    ALTER TYPE salutaionenum RENAME TO salutationenum;
                ELSE
                    CREATE TYPE salutationenum AS ENUM ('Mr', 'Mrs', 'Miss');
                END IF;
            END IF;

            SELECT c.udt_name
            INTO title_type
            FROM information_schema.columns c
            WHERE c.table_schema = current_schema()
              AND c.table_name = 'profile'
              AND c.column_name = 'title';

            IF title_type IS NOT NULL AND title_type <> 'salutationenum' THEN
                ALTER TABLE profile
                    ALTER COLUMN title TYPE salutationenum
                    USING title::text::salutationenum;
            END IF;

            BEGIN
                DROP TYPE IF EXISTS salutaionenum;
            EXCEPTION
                WHEN dependent_objects_still_exist THEN
                    NULL;
            END;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            title_type text;
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'salutaionenum'
            ) THEN
                CREATE TYPE salutaionenum AS ENUM ('Mr', 'Mrs', 'Miss');
            END IF;

            SELECT c.udt_name
            INTO title_type
            FROM information_schema.columns c
            WHERE c.table_schema = current_schema()
              AND c.table_name = 'profile'
              AND c.column_name = 'title';

            IF title_type IS NOT NULL AND title_type <> 'salutaionenum' THEN
                ALTER TABLE profile
                    ALTER COLUMN title TYPE salutaionenum
                    USING title::text::salutaionenum;
            END IF;

            BEGIN
                DROP TYPE IF EXISTS salutationenum;
            EXCEPTION
                WHEN dependent_objects_still_exist THEN
                    NULL;
            END;
        END
        $$;
        """
    )
