"""initial_user_model

Revision ID: ce576cd2faa3
Revises: 
Create Date: 2026-06-13 17:32:41.455593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce576cd2faa3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: create/modify users table only."""
    conn = op.get_bind()
    
    # Check which columns already exist (from a partially applied previous run)
    existing_columns = [row[1] for row in conn.execute(
        sa.text("PRAGMA table_info('users')")
    ).fetchall()]
    
    if 'password_hash' not in existing_columns:
        op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=False, server_default=''))
    if 'phone' not in existing_columns:
        op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    if 'updated_at' not in existing_columns:
        op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Check if hashed_password still exists before dropping
    if 'hashed_password' in existing_columns:
        op.drop_column('users', 'hashed_password')


def downgrade() -> None:
    """Downgrade schema: revert users table only."""
    conn = op.get_bind()
    existing_columns = [row[1] for row in conn.execute(
        sa.text("PRAGMA table_info('users')")
    ).fetchall()]
    
    if 'hashed_password' not in existing_columns:
        op.add_column('users', sa.Column('hashed_password', sa.TEXT(), nullable=False, server_default=''))
    if 'updated_at' in existing_columns:
        op.drop_column('users', 'updated_at')
    if 'phone' in existing_columns:
        op.drop_column('users', 'phone')
    if 'password_hash' in existing_columns:
        op.drop_column('users', 'password_hash')