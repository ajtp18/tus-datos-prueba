"""se agrega el modelo de sesion para manejarlas dentro de la app

Revision ID: 9e3aad577f75
Revises: 12332cdbb1f6
Create Date: 2024-12-09 09:33:28.598882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e3aad577f75'
down_revision: Union[str, None] = '12332cdbb1f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
