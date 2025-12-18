"""add missing user columns

Revision ID: b58fc5ef8432
Revises: 00f5edf076f9
Create Date: 2025-11-22 11:08:16.159984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b58fc5ef8432'
down_revision: Union[str, None] = '00f5edf076f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types first
    verification_status_enum = sa.Enum('PENDING', 'VERIFIED', 'REJECTED', name='verificationstatus')
    verification_status_enum.create(op.get_bind(), checkfirst=True)
    
    account_status_enum = sa.Enum('ACTIVE', 'SUSPENDED', 'DELETED', name='accountstatus')
    account_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Business account fields
    op.add_column('users', sa.Column('is_business_account', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('business_name', sa.String(length=200), nullable=True))
    op.add_column('users', sa.Column('business_category', sa.String(length=100), nullable=True))
    
    # Verification fields
    op.add_column('users', sa.Column('verification_status', verification_status_enum, nullable=True, server_default='PENDING'))
    op.add_column('users', sa.Column('identity_document_type', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('identity_document_number', sa.String(length=50), nullable=True))
    
    # Location fields
    op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(length=100), nullable=True))
    
    # Two factor authentication
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(length=255), nullable=True))
    
    # Account status
    op.add_column('users', sa.Column('account_status', account_status_enum, nullable=True, server_default='ACTIVE'))
    
    # Timestamps
    op.add_column('users', sa.Column('created_at', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'account_status')
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'country')
    op.drop_column('users', 'city')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'identity_document_number')
    op.drop_column('users', 'identity_document_type')
    op.drop_column('users', 'verification_status')
    op.drop_column('users', 'business_category')
    op.drop_column('users', 'business_name')
    op.drop_column('users', 'is_business_account')
    
    # Drop ENUM types
    sa.Enum(name='accountstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='verificationstatus').drop(op.get_bind(), checkfirst=True)

