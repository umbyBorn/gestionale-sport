"""crea tabella ricevute_donazione (erogazioni liberali)

Revision ID: e1f2a3b4c5d6
Revises: d9e0f1a2b3c4
Create Date: 2026-07-12 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, Sequence[str], None] = 'd9e0f1a2b3c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ricevute_donazione',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome_donatore', sa.String(), nullable=False),
        sa.Column('importo', sa.Numeric(10, 2), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('causale', sa.String(), nullable=True),
        sa.Column('creato_il', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ricevute_donazione_id'), 'ricevute_donazione', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ricevute_donazione_id'), table_name='ricevute_donazione')
    op.drop_table('ricevute_donazione')
