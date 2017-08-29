"""Add table for datapath

Revision ID: ce8079bf4ab7
Revises: None
Create Date: 2017-08-26 21:42:40.469444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce8079bf4ab7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'datapath',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('host', sa.String(64), nullable=False),
        sa.Column('port', sa.Integer, nullable=False))

    op.create_table(
        'port',
        sa.Column('datapath_id', sa.String(64), sa.ForeignKey('datapath.id',
                                                              ondelete='CASCADE'),
                  primary_key=True),
        sa.Column('mac', sa.String(64), nullable=False),
        sa.Column('port', sa.String(10), nullable=False, primary_key=True),
        sa.Column('subnet_id', sa.String(36), sa.ForeignKey('subnet.id',
                                                            ondelete='CASCADE'),
                  nullable=False))
