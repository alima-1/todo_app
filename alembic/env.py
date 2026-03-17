from logging.config import fileConfig

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from dotenv import load_dotenv
import os

import pkgutil
import importlib
import app.models  # Point this to your models package
from app.config.database import Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

# escape % in the DATABASE_URL for alembic config parsing so that it doesn't
# treat them as placeholders for config variables but
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("%", "%%")

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def import_all_models(package):
    """Dynamically imports all modules in a given package."""
    for loader, module_name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        importlib.import_module(module_name)


# Trigger the auto-import
import_all_models(app.models)
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
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
    """Run migrations in 'online' mode with an AsyncEngine."""
    # 1. Create the async engine
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
    )

    # 2. Define the synchronous migration logic
    def do_run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

    # 3. Define an async runner to manage the connection
    async def run_async_migrations():
        async with connectable.connect() as connection:
            # run_sync bridges the async connection to the sync context
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    # 4. Execute the async runner
    try:
        asyncio.run(run_async_migrations())
    except Exception as e:
        print(f"Error during migration: {e}")
        raise e


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()  # Call it directly here
