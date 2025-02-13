"""history_match

Revision ID: bdced143ee67
Revises: 1668ffe5fe74
Create Date: 2025-02-13 19:56:55.128874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdced143ee67'
down_revision: Union[str, None] = '1668ffe5fe74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'history_match',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('match_id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.Index('idx_history_match_user_id', 'user_id')
    )


def downgrade() -> None:
    op.drop_table('history_match')
