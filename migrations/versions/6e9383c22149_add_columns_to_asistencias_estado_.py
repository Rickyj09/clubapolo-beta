"""add columns to asistencias (estado, registrado_por, observacion, updated_at)

Revision ID: 6e9383c22149
Revises: 6833b1bae497
Create Date: 2026-01-23 12:45:26.001443

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6e9383c22149'
down_revision = '6833b1bae497'
branch_labels = None
depends_on = None



def upgrade():
    # Nuevas columnas

 
    # FK registrado_por_id -> users.id
 
    # Índice (si ya existe, comenta esta línea)
   

    # Opcional: si ya existe 'presente' y quieres mapearlo a 'estado'
    # P = Presente, A = Ausente
    op.execute("""
        UPDATE asistencias
        SET estado = CASE WHEN presente = 1 THEN 'P' ELSE 'A' END
        WHERE estado IS NULL OR estado = ''
    """)

def downgrade():
    op.drop_index("ix_asistencias_fecha_sucursal", table_name="asistencias")

    op.drop_constraint("fk_asistencias_registrado_por", "asistencias", type_="foreignkey")
    op.drop_column("asistencias", "updated_at")
    op.drop_column("asistencias", "observacion")
    op.drop_column("asistencias", "estado")
    op.drop_column("asistencias", "registrado_por_id")

