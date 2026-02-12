"""whatsapp por sucursal

Revision ID: 3d987c6800c8
Revises: e588488d2f60
Create Date: 2026-02-12 15:16:44.277618

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3d987c6800c8'
down_revision = 'e588488d2f60'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("sucursales", sa.Column("whatsapp_numero", sa.String(length=20), nullable=True))
    op.add_column("sucursales", sa.Column("whatsapp_mensaje", sa.String(length=255), nullable=True))

def downgrade():
    op.drop_column("sucursales", "whatsapp_mensaje")
    op.drop_column("sucursales", "whatsapp_numero")
    # ### end Alembic commands ###
