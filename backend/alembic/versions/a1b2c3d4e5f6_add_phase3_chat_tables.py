"""add_phase3_chat_tables

Revision ID: a1b2c3d4e5f6
Revises: 8335fb1bfb29
Create Date: 2026-01-21 12:00:00.000000

Phase 3: Add conversations and messages tables for AI Chat feature.

Tables added:
- conversations: Chat sessions between users and AI assistant
- messages: Individual messages within conversations

Implements:
- FR-006: Persist conversation history per user session
- FR-010: Log AI interpretations with confidence scores
- FR-013: User data isolation (CASCADE DELETE on user_id FK)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8335fb1bfb29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Phase 3 chat tables: conversations and messages."""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_conversations_user_id'),
        'conversations',
        ['user_id'],
        unique=False
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('conversation_id', sa.Uuid(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column('content', sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=False),
        sa.Column('generated_command', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_messages_conversation_id'),
        'messages',
        ['conversation_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_messages_timestamp'),
        'messages',
        ['timestamp'],
        unique=False
    )


def downgrade() -> None:
    """Remove Phase 3 chat tables."""

    # Drop messages table first (has FK to conversations)
    op.drop_index(op.f('ix_messages_timestamp'), table_name='messages')
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_table('conversations')
