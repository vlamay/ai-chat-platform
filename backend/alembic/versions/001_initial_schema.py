"""Initial schema for AI Chat Platform

Revision ID: 001
Revises:
Create Date: 2026-03-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        # Create users table
        op.create_table(
            'users',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('avatar_url', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    except Exception:
        # Table already exists, skip
        pass

    try:
        # Create chats table
        op.create_table(
            'chats',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('model', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    except Exception:
        # Table already exists, skip
        pass

    try:
        # Create messages table
        op.create_table(
            'messages',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('chat_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('role', sa.String(), nullable=False),
            sa.Column('content', sa.String(), nullable=False),
            sa.Column('tokens_used', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
            sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    except Exception:
        # Table already exists, skip
        pass


def downgrade() -> None:
    try:
        op.drop_table('messages')
    except Exception:
        pass

    try:
        op.drop_table('chats')
    except Exception:
        pass

    try:
        op.drop_index(op.f('ix_users_email'), table_name='users')
    except Exception:
        pass

    try:
        op.drop_table('users')
    except Exception:
        pass
