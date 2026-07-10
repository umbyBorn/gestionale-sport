"""dedup presenze duplicate + vincolo unicità (evento_id, tesserato_id)

Revision ID: c8d9e0f1a2b3
Revises: b7c8d9e0f1a2
Create Date: 2026-07-10 09:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c8d9e0f1a2b3'
down_revision: Union[str, Sequence[str], None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Prima del vincolo, ripulisco eventuali righe duplicate già presenti in
    # produzione (generate dal vecchio endpoint POST /presenze/ non idempotente).
    # Per ogni coppia (evento_id, tesserato_id) tengo solo la riga con id più alto
    # (la più recente), che riflette l'ultima scelta effettuata dall'utente/staff.
    op.execute("""
        DELETE FROM presenze p
        USING presenze p2
        WHERE p.evento_id = p2.evento_id
          AND p.tesserato_id = p2.tesserato_id
          AND p.id < p2.id
    """)

    op.create_unique_constraint(
        'uq_presenza_evento_tesserato', 'presenze', ['evento_id', 'tesserato_id']
    )


def downgrade() -> None:
    op.drop_constraint('uq_presenza_evento_tesserato', 'presenze', type_='unique')
