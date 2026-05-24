"""Agregar defensa personal a examenes

Revision ID: 047924194b1f
Revises: c505d314e4dc
Create Date: 2026-05-23 17:35:30.883485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '047924194b1f'
down_revision = 'c505d314e4dc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'examenes',
        sa.Column('usa_defensa_personal', sa.Boolean(), nullable=True)
    )
    op.add_column(
        'examenes',
        sa.Column('peso_defensa_personal', sa.Numeric(precision=5, scale=2), nullable=True)
    )

    op.add_column(
        'examen_inscripciones',
        sa.Column('nota_defensa_personal', sa.Numeric(precision=5, scale=2), nullable=True)
    )
    op.add_column(
        'examen_inscripciones',
        sa.Column('observacion_defensa_personal', sa.Text(), nullable=True)
    )


def downgrade():
    op.drop_column('examen_inscripciones', 'observacion_defensa_personal')
    op.drop_column('examen_inscripciones', 'nota_defensa_personal')

    op.drop_column('examenes', 'peso_defensa_personal')
    op.drop_column('examenes', 'usa_defensa_personal')
