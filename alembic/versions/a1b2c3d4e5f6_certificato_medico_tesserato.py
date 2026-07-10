"""aggiunta scadenza certificato medico sportivo su tesserati

Revision ID: a1b2c3d4e5f6
Revises: 957aaca85b47
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '957aaca85b47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'tesserati',
        sa.Column('data_scadenza_certificato_medico', sa.Date(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tesserati', 'data_scadenza_certificato_medico')
