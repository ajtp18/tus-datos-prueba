"""empty message

Revision ID: 7d3e6c2e181a
Revises: 9a8b203f16d2
Create Date: 2024-12-09 11:26:52.975332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d3e6c2e181a'
down_revision: Union[str, None] = '9a8b203f16d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'assistant_limit')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('assistant_limit', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
