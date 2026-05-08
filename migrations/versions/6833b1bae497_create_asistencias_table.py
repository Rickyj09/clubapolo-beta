"""create asistencias table

Revision ID: 6833b1bae497
Revises: 3e4b94cfa723
Create Date: 2026-01-23 11:05:58.843057
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6833b1bae497"
down_revision = "3e4b94cfa723"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Crear tabla (define aquí las columnas reales de tu modelo)
    op.create_table(
        "asistencias",
        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("sucursal_id", sa.Integer(), sa.ForeignKey("sucursales.id"), nullable=False),

        # Si tu asistencia es por alumno:
        sa.Column("alumno_id", sa.Integer(), sa.ForeignKey("alumnos.id"), nullable=False),

        # Opcionales típicos:
        sa.Column("presente", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # 2) Crear índice DESPUÉS de la tabla
    op.create_index(
        "ix_asistencias_fecha_sucursal",
        "asistencias",
        ["fecha", "sucursal_id"],
    )


def downgrade():
    op.drop_index("ix_asistencias_fecha_sucursal", table_name="asistencias")
    op.drop_table("asistencias")
