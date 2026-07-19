"""crea tabella documenti_socio (upload multipli moduli/documenti per socio)

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f8
Create Date: 2026-07-19 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b4c5d6e7f8a9'
down_revision: Union[str, Sequence[str], None] = 'a3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'documenti_socio',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('staff_id', sa.Integer(), sa.ForeignKey('staff.id'), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('nome_file', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('data_caricamento', sa.Date(), nullable=False),
        sa.Column('note', sa.String(), nullable=True),
    )
    # Migro l'eventuale modulo firmato già caricato col vecchio sistema
    # (singolo path_modulo_firmato) nella nuova tabella, per non perderlo.
    op.execute("""
        INSERT INTO documenti_socio (staff_id, tipo, nome_file, url, data_caricamento)
        SELECT id, 'Modulo di adesione firmato', 'modulo_firmato.pdf', path_modulo_firmato, CURRENT_DATE
        FROM staff
        WHERE path_modulo_firmato IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_table('documenti_socio')
