"""estensione contabilita: descrizione, evento, batch e collegamento prima nota

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-09 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pagamenti', sa.Column('descrizione', sa.String(), nullable=True))
    op.add_column('pagamenti', sa.Column('evento_id', sa.Integer(), nullable=True))
    op.add_column('pagamenti', sa.Column('gruppo_generazione_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_pagamenti_gruppo_generazione_id'), 'pagamenti', ['gruppo_generazione_id'], unique=False)
    op.create_foreign_key(op.f('pagamenti_evento_id_fkey'), 'pagamenti', 'eventi', ['evento_id'], ['id'])

    op.add_column('movimenti_contabili', sa.Column('pagamento_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('movimenti_contabili_pagamento_id_fkey'), 'movimenti_contabili', 'pagamenti', ['pagamento_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint(op.f('movimenti_contabili_pagamento_id_fkey'), 'movimenti_contabili', type_='foreignkey')
    op.drop_column('movimenti_contabili', 'pagamento_id')

    op.drop_constraint(op.f('pagamenti_evento_id_fkey'), 'pagamenti', type_='foreignkey')
    op.drop_index(op.f('ix_pagamenti_gruppo_generazione_id'), table_name='pagamenti')
    op.drop_column('pagamenti', 'gruppo_generazione_id')
    op.drop_column('pagamenti', 'evento_id')
    op.drop_column('pagamenti', 'descrizione')
