"""unique pagos by tenant alumno mes anio

Revision ID: 5a9ed46e2a97
Revises: 57cde6a1eaa3
Create Date: 2026-02-09 14:30:42.118643
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5a9ed46e2a97"
down_revision = "57cde6a1eaa3"
branch_labels = None
depends_on = None


def _uq_exists(table, uq_name):
    bind = op.get_bind()
    row = bind.execute(
        sa.text("""
            SELECT CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = DATABASE()
              AND TABLE_NAME = :t
              AND CONSTRAINT_NAME = :c
              AND CONSTRAINT_TYPE = 'UNIQUE'
        """),
        {"t": table, "c": uq_name},
    ).fetchone()
    return row is not None


def upgrade():
    # ==========================================================
    # PAGOS: UNIQUE por academia + alumno + año + mes
    # ==========================================================
    with op.batch_alter_table("pagos", schema=None) as batch_op:
        if not _uq_exists("pagos", "uq_pago_tenant_alumno_anio_mes"):
            batch_op.create_unique_constraint(
                "uq_pago_tenant_alumno_anio_mes",
                ["academia_id", "alumno_id", "anio", "mes"]
            )


def downgrade():
    # (Opcional) rollback seguro
    with op.batch_alter_table("pagos", schema=None) as batch_op:
        if _uq_exists("pagos", "uq_pago_tenant_alumno_anio_mes"):
            batch_op.drop_constraint(
                "uq_pago_tenant_alumno_anio_mes",
                type_="unique"
            )