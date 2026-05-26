"""Agregar token de cuestionario publico

Revision ID: 9b7c31a4d2f0
Revises: 6a8a1f41f0c2
Create Date: 2026-05-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b7c31a4d2f0"
down_revision = "6a8a1f41f0c2"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("examen_inscripciones", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cuestionario_token", sa.String(length=128), nullable=True))
        batch_op.add_column(
            sa.Column(
                "cuestionario_estado",
                sa.String(length=20),
                nullable=False,
                server_default="PENDIENTE",
            )
        )
        batch_op.add_column(sa.Column("cuestionario_respondido_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("cuestionario_expires_at", sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint(
            "uq_examen_inscripciones_cuestionario_token",
            ["cuestionario_token"],
        )

    with op.batch_alter_table("examen_inscripciones", schema=None) as batch_op:
        batch_op.alter_column("cuestionario_estado", server_default=None)


def downgrade():
    with op.batch_alter_table("examen_inscripciones", schema=None) as batch_op:
        batch_op.drop_constraint("uq_examen_inscripciones_cuestionario_token", type_="unique")
        batch_op.drop_column("cuestionario_expires_at")
        batch_op.drop_column("cuestionario_respondido_at")
        batch_op.drop_column("cuestionario_estado")
        batch_op.drop_column("cuestionario_token")
