"""add_rssi_thresholds

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2026-06-02 17:21:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. server_default를 사용하여 기존 row에 기본값이 들어가도록 컬럼 추가
    with op.batch_alter_table('spaces', schema=None) as batch_op:
        batch_op.add_column(sa.Column('wifi_rssi_threshold', sa.Integer(), server_default='-75', nullable=False))
        batch_op.add_column(sa.Column('bt_rssi_threshold', sa.Integer(), server_default='-70', nullable=False))

    # 2. (선택적) 백필 후 server_default 속성 제거
    with op.batch_alter_table('spaces', schema=None) as batch_op:
        batch_op.alter_column('wifi_rssi_threshold', server_default=None)
        batch_op.alter_column('bt_rssi_threshold', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('spaces', schema=None) as batch_op:
        batch_op.drop_column('bt_rssi_threshold')
        batch_op.drop_column('wifi_rssi_threshold')
