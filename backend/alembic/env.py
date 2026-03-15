"""Alembic environment configuration for async SQLAlchemy."""
import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

# Import models for autogenerate
from app.core.database import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database URL from environment or use config
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Set target metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Execute migrations with async connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    import logging
    migration_logger = logging.getLogger("alembic.runtime.migration")

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv(
        "DATABASE_URL", configuration.get("sqlalchemy.url", "")
    )

    migration_logger.info(f"Running migrations on database: {configuration['sqlalchemy.url']}")

    try:
        connectable = create_async_engine(
            configuration["sqlalchemy.url"],
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
            migration_logger.info("Migrations completed successfully")

        await connectable.dispose()
    except Exception as e:
        migration_logger.error(f"Migration error (continuing): {str(e)}")
        # Don't raise - let app start anyway


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
