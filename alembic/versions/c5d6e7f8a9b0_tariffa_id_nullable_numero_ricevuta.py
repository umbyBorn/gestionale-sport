"""tariffa_id nullable su pagamenti + numero_ricevuta dedicato

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2026-07-20 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c5d6e7f8a9b0'
down_revision: Union[str, Sequence[str], None] = 'b4c5d6e7f8a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('pagamenti', 'tariffa_id', existing_type=sa.Integer(), nullable=True)
    op.add_column('pagamenti', sa.Column('numero_ricevuta', sa.Integer(), nullable=True))
    op.create_unique_constraint('uq_pagamenti_numero_ricevuta', 'pagamenti', ['numero_ricevuta'])


def downgrade() -> None:
    op.drop_constraint('uq_pagamenti_numero_ricevuta', 'pagamenti', type_='unique')
    op.drop_column('pagamenti', 'numero_ricevuta')
    op.alter_column('pagamenti', 'tariffa_id', existing_type=sa.Integer(), nullable=False)
