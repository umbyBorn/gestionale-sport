"""aggiunto ruolo operatore

Revision ID: 5c007a67cf95
Revises: 848fc3462d65
Create Date: 2026-07-02

"""
from typing import Sequence, Union
from alembic import op

revision: str = '5c007a67cf95'
down_revision: Union[str, Sequence[str], None] = '848fc3462d65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE ruoloenum ADD VALUE IF NOT EXISTS 'operatore'")


def downgrade() -> None:
    pass
