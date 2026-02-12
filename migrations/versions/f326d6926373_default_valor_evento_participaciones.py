"""default valor_evento participaciones

Revision ID: f326d6926373
Revises: fd634d42e9a8
Create Date: ...

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f326d6926373"
down_revision = "fd634d42e9a8"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Si ya existen registros con NULL, primero normaliza
    op.execute("UPDATE participaciones SET valor_evento = 0 WHERE valor_evento IS NULL")

    # 2) Pon DEFAULT y NOT NULL (ajusta el tipo según tu columna real)
    op.alter_column(
        "participaciones",
        "valor_evento",
        existing_type=sa.Integer(),          # <-- cambia a sa.Numeric(...) si aplica
        nullable=False,
        server_default="0",
    )


def downgrade():
    # Quita default (si quieres) y permite NULL (opcional)
    op.alter_column(
        "participaciones",
        "valor_evento",
        existing_type=sa.Integer(),          # <-- igual que arriba
        nullable=True,
        server_default=None,
    )