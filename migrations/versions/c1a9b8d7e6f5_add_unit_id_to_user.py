# c:\condomanager-saas\migrations\versions\c1a9b8d7e6f5_add_unit_id_to_user.py
"""add unit_id to user

Revision ID: c1a9b8d7e6f5
Revises: 
Create Date: 2025-11-21 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c1a9b8d7e6f5'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unit_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_users_unit_id_units', 'units', ['unit_id'], ['id'])

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_unit_id_units', type_='foreignkey')
        batch_op.drop_column('unit_id')
