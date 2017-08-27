"""create tables for dhcp

Revision ID: a76fea54e273
Revises: ce8079bf4ab7
Create Date: 2017-08-19 20:47:08.004224

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


# revision identifiers, used by Alembic.
revision = 'a76fea54e273'
down_revision = 'ce8079bf4ab7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'subnet',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('network', sa.String(64), nullable=False),
        sa.Column('cidr', sa.Integer, nullable=False),
        sa.Column('gateway', sa.String(64), nullable=False),
        sa.Column('server', sa.String(64), sa.ForeignKey('reserved_ip.ip',
                                                         ondelete='CASCADE'),
                  nullable=True))

    op.create_table(
        'ip_range',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('subnet_id', sa.String(36), sa.ForeignKey('subnet.id',
                                                            ondelete='CASCADE'),
                  nullable=False),
        sa.Column('start_ip', sa.String(64), nullable=False),
        sa.Column('end_ip', sa.String(64), nullable=False))

    op.create_table(
        'parameter',
        sa.Column('subnet_id', sa.String(36), sa.ForeignKey('subnet.id',
                                                            ondelete='CASCADE'),
                  nullable=False, primary_key=True),
        sa.Column('mac', sa.String(36), sa.ForeignKey('ReservedIP.mac',
                                                      ondelete='CASCADE'),
                  nullable=True, primary_key=True),
        sa.Column('data', sa.PickleType, nullable=True, primary_key=True))

    op.create_table(
        'reserved_ip',
        sa.Column('ip', sa.String(64), nullable=False),
        sa.Column('mac', sa.String(36), nullable=False, primary_key=True),
        sa.Column('subnet_id', sa.String(36), sa.ForeignKey('subnet.id',
                                                            ondelete='CASCADE'),
                  nullable=False, primary_key=True),
        sa.Column('is_reserved', sa.Boolean(), nullable=False,
                  server_default=sa.sql.false()),
        sa.Column('interface', sa.String(10), nullable=True),
        sa.Column('lease_time', sa.TIMESTAMP, nullable=True),
        sa.Column('renew_time', sa.TIMESTAMP, nullable=True),
        sa.Column('expiry_time', sa.TIMESTAMP, nullable=True))
