"""Add forum post model

Revision ID: 966ee5623d5b
Revises: 3fdf00fb7aed
Create Date: 2024-10-21 00:06:07.825633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '966ee5623d5b'
down_revision = '3fdf00fb7aed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('forum_post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('date_posted', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('forum_post')
    # ### end Alembic commands ###