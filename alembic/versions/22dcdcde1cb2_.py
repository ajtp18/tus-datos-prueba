"""Seed default roles

Revision ID: 22dcdcde1cb2
Revises: 39e5b3cf50a0
Create Date: 2024-12-05 19:49:05.195302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from tus_datos_prueba.models import Role, RolePerm
from slugify import slugify

# revision identifiers, used by Alembic.
revision: str = '22dcdcde1cb2'
down_revision: Union[str, None] = '39e5b3cf50a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

roles = [
    {
        "role": "Administrator",
        "permissions": [
            {
                "resource": "user",
                "verbs": ["create", "update_me", "update", "get", "list", "delete"]
            },
            {
                "resource": "user/password",
                "verbs": ["change_me", "change", "delete"]
            },
            {
                "resource": "roles",
                "verbs": ["create", "update", "get", "list", "delete"]
            },
            {
                "resource": "events",
                "verbs": ["create", "update", "get", "list", "delete"]
            },
            {
                "resource": "assistants",
                "verbs": ["create", "update", "get", "list", "delete"]
            },
        ],
    },
    {
        "role": "User",
        "permissions": [
            {
                "resource": "user",
                "verbs": ["update_me", "get", "list"]
            },
            {
                "resource": "user/password",
                "verbs": ["change_me"]
            },
            {
                "resource": "roles",
                "verbs": ["get"]
            },
            {
                "resource": "events",
                "verbs": ["create", "update", "get", "list", "delete"]
            },
            {
                "resource": "assistants",
                "verbs": ["create", "update", "get", "list", "delete"]
            },
        ],
    },
]

def upgrade() -> None:
    connection = op.get_bind()
    session = Session(bind=connection)

    role_models = list()
    for role in roles:
        perms = [RolePerm(**perm) for perm in role["permissions"]]
        _role = Role(role=role["role"], role_slug=slugify(role["role"]), permissions=perms)

        role_models.append(_role)
    
    session.add_all(role_models)
    session.commit()


def downgrade() -> None:
    connection = op.get_bind()
    session = Session(bind=connection)

    role_names = [slugify(role["role"]) for role in roles]

    session.query(Role).filter(Role.role_slug.in_(role_names)).delete(synchronize_session="fetch")

    session.commit()


