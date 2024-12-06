"""Add created_by_id column to events

Revision ID: 3d988a85a964
Revises: 98bf771ad783
Create Date: 2024-12-05 18:35:33.823193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d988a85a964'
down_revision: Union[str, None] = '98bf771ad783'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('created_by_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'events', 'users', ['created_by_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.drop_column('events', 'created_by_id')
    # ### end Alembic commands ###
