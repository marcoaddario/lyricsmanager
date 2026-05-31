"""add service card columns to setlist_items

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-03 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('setlist_items', 'song_id', nullable=True)
    op.add_column('setlist_items', sa.Column('is_service_card', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('setlist_items', sa.Column('service_card_text', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('setlist_items', 'service_card_text')
    op.drop_column('setlist_items', 'is_service_card')
    # Reset songs with null song_id before making non-nullable again
    op.execute("DELETE FROM setlist_items WHERE song_id IS NULL")
    op.alter_column('setlist_items', 'song_id', nullable=False)
