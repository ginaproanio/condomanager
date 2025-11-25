"""Add billing_contact and document codes

Revision ID: 3f4e3d49af73
Revises: 396bbea0d11c
Create Date: 2025-11-24 22:35:53.954335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f4e3d49af73'
down_revision = '396bbea0d11c'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add document_code_prefix to condominiums
    with op.batch_alter_table('condominiums', schema=None) as batch_op:
        batch_op.add_column(sa.Column('document_code_prefix', sa.String(length=10), nullable=True))
        # We assume billing_contact_id was NOT added successfully by the failed migration, so we add it here
        batch_op.add_column(sa.Column('billing_contact_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_condominium_billing_contact', 'users', ['billing_contact_id'], ['id'])

    # 2. Add document_code to documents
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('document_code', sa.String(length=50), nullable=True))
        batch_op.create_unique_constraint('uq_document_code', ['document_code'])


def downgrade():
    with op.batch_alter_table('documents', schema=None) as batch_op:
        batch_op.drop_constraint('uq_document_code', type_='unique')
        batch_op.drop_column('document_code')

    with op.batch_alter_table('condominiums', schema=None) as batch_op:
        batch_op.drop_constraint('fk_condominium_billing_contact', type_='foreignkey')
        batch_op.drop_column('billing_contact_id')
        batch_op.drop_column('document_code_prefix')
