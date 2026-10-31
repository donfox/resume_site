"""add request count and last requested time to email_request

Revision ID: a4a064950899
Revises: cd175d0002b4
Create Date: 2026-10-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4a064950899'
down_revision = 'cd175d0002b4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('email_request') as batch_op:
        batch_op.add_column(sa.Column('request_count', sa.Integer(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('last_requested_at', sa.DateTime(), nullable=True))
    # Existing rows: no repeats were recorded, so last request = first request
    op.execute('UPDATE email_request SET last_requested_at = timestamp')


def downgrade():
    with op.batch_alter_table('email_request') as batch_op:
        batch_op.drop_column('last_requested_at')
        batch_op.drop_column('request_count')
