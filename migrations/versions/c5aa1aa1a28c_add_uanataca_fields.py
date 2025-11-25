"""add uanataca fields

Revision ID: c5aa1aa1a28c
Revises: f6b455b52673
Create Date: 2025-11-25 15:09:52.863134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5aa1aa1a28c'
down_revision = 'f6b455b52673'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('condominiums', schema=None) as batch_op:
        batch_op.add_column(sa.Column('signature_provider_config', sa.JSON(), nullable=True))

    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('external_flow_id', sa.String(length=100), nullable=True))


def downgrade():
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_column('external_flow_id')

    with op.batch_alter_table('condominiums', schema=None) as batch_op:
        batch_op.drop_column('signature_provider_config')
