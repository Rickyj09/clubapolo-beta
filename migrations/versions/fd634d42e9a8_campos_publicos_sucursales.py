from alembic import op
import sqlalchemy as sa

revision = 'fd634d42e9a8'
down_revision = '6e9383c22149'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('sucursales') as batch_op:
        batch_op.add_column(sa.Column('resumen_publico', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('google_maps_url', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('foto_1', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('foto_2', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('foto_3', sa.String(length=255), nullable=True))

def downgrade():
    with op.batch_alter_table('sucursales') as batch_op:
        batch_op.drop_column('foto_3')
        batch_op.drop_column('foto_2')
        batch_op.drop_column('foto_1')
        batch_op.drop_column('google_maps_url')
        batch_op.drop_column('resumen_publico')