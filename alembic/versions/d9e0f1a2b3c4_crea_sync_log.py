"""crea tabella sync_log per funzionamento offline

Revision ID: d9e0f1a2b3c4
Revises: c8d9e0f1a2b3
Create Date: 2026-07-11 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd9e0f1a2b3c4'
down_revision: Union[str, Sequence[str], None] = 'c8d9e0f1a2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sync_log',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('tabella', sa.String(), nullable=False, index=True),
        sa.Column('record_id', sa.Integer(), nullable=False, index=True),
        sa.Column('operazione', sa.String(), nullable=False),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        sa.Column('sincronizzato', sa.Boolean(), nullable=False, server_default=sa.false(), index=True),
        sa.Column('origine', sa.String(), nullable=False, server_default='online'),
    )


def downgrade() -> None:
    op.drop_table('sync_log')
