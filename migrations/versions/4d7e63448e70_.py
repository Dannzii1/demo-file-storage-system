"""empty message

Revision ID: 4d7e63448e70
Revises: 
Create Date: 2022-01-14 09:45:38.844186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d7e63448e70'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('email_address', sa.String(length=255), nullable=True),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('last_reset_token', sa.String(length=255), nullable=True),
    sa.Column('token_used', sa.Boolean(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email_address', name=op.f('uq_users_email_address')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username'))
    )
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('relative_location', sa.String(length=255), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_documents_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_documents'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('documents')
    op.drop_table('users')
    # ### end Alembic commands ###
