"""Add responded field to Response model and number to Poll model

Revision ID: 3fdf00fb7aed
Revises: 
Create Date: 2023-10-19 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3fdf00fb7aed'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add 'responded' column to Response table, allowing null values initially
    with op.batch_alter_table('response', schema=None) as batch_op:
        batch_op.add_column(sa.Column('responded', sa.Boolean(), nullable=True))
    
    # Update existing records to set 'responded' to True
    op.execute("UPDATE response SET responded = TRUE")
    
    # Now set 'responded' column to not null
    with op.batch_alter_table('response', schema=None) as batch_op:
        batch_op.alter_column('responded', nullable=False)
    
    # Add 'number' column to Poll table
    with op.batch_alter_table('poll', schema=None) as batch_op:
        batch_op.add_column(sa.Column('number', sa.Integer(), nullable=True))
    
    # Update existing polls with a number
    op.execute("""
    UPDATE poll
    SET number = subquery.row_num
    FROM (
        SELECT id, ROW_NUMBER() OVER (ORDER BY id) as row_num
        FROM poll
    ) AS subquery
    WHERE poll.id = subquery.id
    """)
    
    # Now set 'number' column to not null and unique
    with op.batch_alter_table('poll', schema=None) as batch_op:
        batch_op.alter_column('number', nullable=False)
        batch_op.create_unique_constraint('uq_poll_number', ['number'])

def downgrade():
    with op.batch_alter_table('response', schema=None) as batch_op:
        batch_op.drop_column('responded')
    
    with op.batch_alter_table('poll', schema=None) as batch_op:
        batch_op.drop_constraint('uq_poll_number', type_='unique')
        batch_op.drop_column('number')
