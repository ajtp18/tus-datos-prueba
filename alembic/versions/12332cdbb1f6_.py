"""Create default admin user

Revision ID: 12332cdbb1f6
Revises: 22dcdcde1cb2
Create Date: 2024-12-05 20:25:47.170299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from tus_datos_prueba.models import Role, User, UserPassword
from tus_datos_prueba.utils.password import create_password


# revision identifiers, used by Alembic.
revision: str = '12332cdbb1f6'
down_revision: Union[str, None] = '22dcdcde1cb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    session = Session(bind=connection)

    role = session.query(Role).where(Role.role_slug == "administrator").first()

    _user = User(
        email="admin@admin.com",
        role=role,
        passwords=[UserPassword(password=create_password("password"))]
    )

    session.add(_user)

    session.commit()


def downgrade() -> None:
    connection = op.get_bind()
    session = Session(bind=connection)

    session.query(User).where(User.email == "admin@admin.com").limit(1).delete(synchronize_session="fetch")

    session.commit()
