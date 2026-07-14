"""crea tabella documenti_societari

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-07-12 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f2a3b4c5d6e7'
down_revision: Union[str, Sequence[str], None] = 'e1f2a3b4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'documenti_societari',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('categoria', sa.String(), nullable=True),
        sa.Column('nome_file', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('data_caricamento', sa.Date(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_documenti_societari_id'), 'documenti_societari', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_documenti_societari_id'), table_name='documenti_societari')
    op.drop_table('documenti_societari')
