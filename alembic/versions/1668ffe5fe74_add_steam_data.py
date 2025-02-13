"""add_steam_data

Revision ID: 1668ffe5fe74
Revises: c9eb103c5d60
Create Date: 2025-02-13 13:52:23.839572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1668ffe5fe74'
down_revision: Union[str, None] = 'c9eb103c5d60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('steamid', sa.String(), nullable=True))
    op.add_column('users', sa.Column('communityvisibilitystate', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('profilestate', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('personaname', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('commentpermission', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('profileurl', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatar', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatarmedium', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatarfull', sa.String(), nullable=True))
    op.add_column('users', sa.Column('avatarhash', sa.String(), nullable=True))
    op.add_column('users', sa.Column('lastlogoff', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('personastate', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('realname', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('primaryclanid', sa.String(), nullable=True))
    op.add_column('users', sa.Column('timecreated', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('personastateflags', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('loccountrycode', sa.String(2), nullable=True))
    op.add_column('users', sa.Column('locstatecode', sa.String(2), nullable=True))
    op.add_column('users', sa.Column('loccityid', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'loccityid')
    op.drop_column('users', 'locstatecode')
    op.drop_column('users', 'loccountrycode')
    op.drop_column('users', 'personastateflags')
    op.drop_column('users', 'timecreated')
    op.drop_column('users', 'primaryclanid')
    op.drop_column('users', 'realname')
    op.drop_column('users', 'personastate')
    op.drop_column('users', 'lastlogoff')
    op.drop_column('users', 'avatarhash')
    op.drop_column('users', 'avatarfull')
    op.drop_column('users', 'avatarmedium')
    op.drop_column('users', 'avatar')
    op.drop_column('users', 'profileurl')
    op.drop_column('users', 'commentpermission')
    op.drop_column('users', 'personaname')
    op.drop_column('users', 'profilestate')
    op.drop_column('users', 'communityvisibilitystate')
    op.drop_column('users', 'steamid')