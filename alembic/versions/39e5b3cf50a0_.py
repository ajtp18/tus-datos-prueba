"""Create assistants table

Revision ID: 39e5b3cf50a0
Revises: 3d988a85a964
Create Date: 2024-12-05 18:45:38.271372

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39e5b3cf50a0'
down_revision: Union[str, None] = '3d988a85a964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assistants',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('type', sa.Enum('STAFF', 'SPEAKER', 'MAINTAINENCE', 'USER', 'OWNER', name='assistanttype'), nullable=False),
    sa.Column('contact_meta', sa.JSON(none_as_null=True), nullable=True),
    sa.Column('meta', sa.JSON(none_as_null=True), nullable=True),
    sa.Column('event_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assistants_email'), 'assistants', ['email'], unique=False)
    op.create_index(op.f('ix_assistants_event_id'), 'assistants', ['event_id'], unique=False)
    op.create_index(op.f('ix_assistants_user_id'), 'assistants', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_assistants_user_id'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_event_id'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_email'), table_name='assistants')
    op.drop_table('assistants')
    # ### end Alembic commands ###