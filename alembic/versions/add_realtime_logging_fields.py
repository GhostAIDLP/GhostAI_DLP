"""add realtime logging fields

Revision ID: add_realtime_logging_fields
Revises: 092a2a33efbe
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_realtime_logging_fields'
down_revision: Union[str, Sequence[str], None] = '092a2a33efbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add real-time logging fields to dlp_findings table."""
    # Add new columns for real-time logging
    op.add_column('dlp_findings', sa.Column('session_id', sa.String(length=255), nullable=True))
    op.add_column('dlp_findings', sa.Column('input_hash', sa.String(length=64), nullable=True))
    op.add_column('dlp_findings', sa.Column('flags', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('dlp_findings', sa.Column('latency_ms', sa.Float(), nullable=True))
    op.add_column('dlp_findings', sa.Column('environment', sa.String(length=50), nullable=True))
    op.add_column('dlp_findings', sa.Column('user_agent', sa.Text(), nullable=True))
    op.add_column('dlp_findings', sa.Column('ip_address', sa.String(length=45), nullable=True))
    op.add_column('dlp_findings', sa.Column('encrypted_reasons', sa.Text(), nullable=True))
    op.add_column('dlp_findings', sa.Column('is_encrypted', sa.Boolean(), nullable=True, default=False))
    
    # Create indexes for performance
    op.create_index('ix_dlp_findings_session_id', 'dlp_findings', ['session_id'])
    op.create_index('ix_dlp_findings_input_hash', 'dlp_findings', ['input_hash'])
    op.create_index('ix_dlp_findings_created_at', 'dlp_findings', ['created_at'])


def downgrade() -> None:
    """Remove real-time logging fields from dlp_findings table."""
    # Drop indexes
    op.drop_index('ix_dlp_findings_created_at', table_name='dlp_findings')
    op.drop_index('ix_dlp_findings_input_hash', table_name='dlp_findings')
    op.drop_index('ix_dlp_findings_session_id', table_name='dlp_findings')
    
    # Drop columns
    op.drop_column('dlp_findings', 'is_encrypted')
    op.drop_column('dlp_findings', 'encrypted_reasons')
    op.drop_column('dlp_findings', 'ip_address')
    op.drop_column('dlp_findings', 'user_agent')
    op.drop_column('dlp_findings', 'environment')
    op.drop_column('dlp_findings', 'latency_ms')
    op.drop_column('dlp_findings', 'flags')
    op.drop_column('dlp_findings', 'input_hash')
    op.drop_column('dlp_findings', 'session_id')
