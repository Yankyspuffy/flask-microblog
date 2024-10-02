"""merge heads

Revision ID: 5cbc64221077
Revises: 2a4a3f91498d, 90378c3e5f96
Create Date: 2024-03-05 12:32:58.542899

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cbc64221077'
down_revision = ('2a4a3f91498d', '90378c3e5f96')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
