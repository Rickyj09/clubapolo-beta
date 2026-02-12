from alembic import op
import sqlalchemy as sa

revision = "e588488d2f60"
down_revision = "f326d6926373"
branch_labels = None
depends_on = None


def upgrade():
    # SOLO sucursales: redes sociales
    op.add_column("sucursales", sa.Column("facebook_url", sa.String(length=255), nullable=True))
    op.add_column("sucursales", sa.Column("instagram_url", sa.String(length=255), nullable=True))
    op.add_column("sucursales", sa.Column("youtube_url", sa.String(length=255), nullable=True))
    # opcional:
    # op.add_column("sucursales", sa.Column("tiktok_url", sa.String(length=255), nullable=True))
    # op.add_column("sucursales", sa.Column("web_url", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("sucursales", "youtube_url")
    op.drop_column("sucursales", "instagram_url")
    op.drop_column("sucursales", "facebook_url")
    # opcional:
    # op.drop_column("sucursales", "tiktok_url")
    # op.drop_column("sucursales", "web_url")