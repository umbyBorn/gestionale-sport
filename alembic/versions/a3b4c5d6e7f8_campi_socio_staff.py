"""campi socio su staff + flag emetti_ricevuta su pagamenti

Revision ID: a3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-07-16 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, Sequence[str], None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('staff', sa.Column('indirizzo', sa.String(), nullable=True))
    op.add_column('staff', sa.Column('comune_residenza', sa.String(), nullable=True))
    op.add_column('staff', sa.Column('numero_tessera', sa.Integer(), nullable=True))
    op.add_column('staff', sa.Column('data_emissione_tessera', sa.Date(), nullable=True))
    op.add_column('staff', sa.Column('quota_associativa', sa.Numeric(10, 2), nullable=True, server_default='5'))
    op.add_column('staff', sa.Column('quota_pagata', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('staff', sa.Column('path_modulo_firmato', sa.String(), nullable=True))
    op.add_column('staff', sa.Column('tesserato_origine_id', sa.Integer(), sa.ForeignKey('tesserati.id'), nullable=True))
    op.create_unique_constraint('uq_staff_numero_tessera', 'staff', ['numero_tessera'])

    op.add_column('pagamenti', sa.Column('emetti_ricevuta', sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    op.drop_column('pagamenti', 'emetti_ricevuta')
    op.drop_constraint('uq_staff_numero_tessera', 'staff', type_='unique')
    op.drop_column('staff', 'tesserato_origine_id')
    op.drop_column('staff', 'path_modulo_firmato')
    op.drop_column('staff', 'quota_pagata')
    op.drop_column('staff', 'quota_associativa')
    op.drop_column('staff', 'data_emissione_tessera')
    op.drop_column('staff', 'numero_tessera')
    op.drop_column('staff', 'comune_residenza')
    op.drop_column('staff', 'indirizzo')
