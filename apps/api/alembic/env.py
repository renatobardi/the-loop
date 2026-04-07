"""Alembic environment configuration with async and sync support."""

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add the parent directory to sys.path so that 'src' can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapters.postgres.models import Base
from src.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:  # type: ignore[no-untyped-def]
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_sync() -> None:
    """Run migrations synchronously (used in CI/CD with psycopg2)."""
    url = config.get_main_option("sqlalchemy.url")

    # Use NullPool for CI environments to avoid connection issues
    engine = create_engine(url, poolclass=pool.NullPool)

    with engine.connect() as connection:
        do_run_migrations(connection)

    engine.dispose()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations online, choosing sync or async based on driver."""
    url = config.get_main_option("sqlalchemy.url")

    # If URL is sync (postgresql://, not postgresql+asyncpg://), use sync engine
    if "+asyncpg" not in url and "postgresql://" in url:
        run_migrations_sync()
    else:
        # Use async engine for async drivers
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
