"""
Alembic environment configuration for database migrations
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import settings and base
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.models.base import Base

# Import all models to ensure they are registered with Base.metadata
from app.models.location import Location
from app.models.tax_data import TaxData
from app.models.user import User
from app.models.category import Category
from app.models.content import Content
from app.models.hashtag import Hashtag, ContentHashtag
from app.models.content_metrics import ContentMetrics
from app.models.multimedia_file import MultimediaFile, FileVersion
from app.models.transcoding_job import (
    TranscodingJob, TranscodingProfile, TranscodingQueue, TranscodingLog
)
from app.models.follow import Follow
from app.models.like import Like
from app.models.comment import Comment
from app.models.monetizable_action import MonetizableAction
from app.models.interaction import Interaction
from app.models.transaction import Transaction
from app.models.payment_distribution import PaymentDistribution, DistributionLevel
from app.models.voucher import Voucher
from app.models.multiplier_plan import MultiplierPlan, UserPlan
from app.models.notification import Notification
from app.models.feed_item import FeedItem
from app.models.user_preferences import UserPreferences, UserCategory
from app.models.event_fund import EventFund
from app.models.advertising_campaign import AdvertisingCampaign, SalesCommission
from app.models.email_verification import EmailVerification
from app.models.two_factor_auth import TwoFactorAuth, TwoFactorCode
from app.models.password_reset import PasswordReset

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url with DATABASE_URL from settings
if settings.DATABASE_URL:
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
else:
    # If DATABASE_URL is not set, use a default SQLite database for migrations
    # This allows generating migrations without a database connection
    import os
    default_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{default_db_path}")
    print(f"Warning: DATABASE_URL not set. Using default SQLite database: {default_db_path}")

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

