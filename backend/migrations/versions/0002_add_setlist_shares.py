"""add setlist_shares table

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'setlist_shares',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('setlist_id', sa.Integer(), sa.ForeignKey('setlists.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('shared_with_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('permission', sa.String(10), nullable=False, default='view'),
        sa.Column('shared_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('setlist_id', 'shared_with_user_id'),
    )


def downgrade():
    op.drop_table('setlist_shares')
