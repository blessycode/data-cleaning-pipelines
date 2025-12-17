from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add project root to PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

# Import models and settings
try:
    from api.db_models import Base
    from api.config import settings
except ImportError:
    from db_models import Base
    from config import settings

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ------------------------------------------------------------------
# FORCE SYNCHRONOUS DATABASE URL FOR ALEMBIC
# ------------------------------------------------------------------

raw_database_url = os.getenv(
    "DATABASE_URL",
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# If async driver is provided, replace it with sync driver
if raw_database_url.startswith("postgresql+asyncpg://"):
    database_url = raw_database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )
else:
    database_url = raw_database_url

config.set_main_option("sqlalchemy.url", database_url)

# Metadata for autogenerate
target_metadata = Base.metadata

# ------------------------------------------------------------------
# OFFLINE MIGRATIONS
# ------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# ------------------------------------------------------------------
# ONLINE MIGRATIONS
# ------------------------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

# ------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
