"""Agregar campos de gestion a plantillas de examen

Revision ID: 6a8a1f41f0c2
Revises: 047924194b1f
Create Date: 2026-05-23 19:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6a8a1f41f0c2"
down_revision = "047924194b1f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("plantillas_examen", sa.Column("descripcion", sa.Text(), nullable=True))
    op.add_column(
        "plantillas_examen",
        sa.Column("puntaje_minimo", sa.Numeric(precision=5, scale=2), nullable=True),
    )

    op.add_column(
        "plantilla_preguntas",
        sa.Column("puntaje", sa.Numeric(precision=6, scale=2), nullable=True),
    )
    op.add_column(
        "plantilla_preguntas",
        sa.Column("obligatorio", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "plantilla_preguntas",
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.alter_column("plantilla_preguntas", "obligatorio", server_default=None)
    op.alter_column("plantilla_preguntas", "activo", server_default=None)


def downgrade():
    op.drop_column("plantilla_preguntas", "activo")
    op.drop_column("plantilla_preguntas", "obligatorio")
    op.drop_column("plantilla_preguntas", "puntaje")

    op.drop_column("plantillas_examen", "puntaje_minimo")
    op.drop_column("plantillas_examen", "descripcion")
