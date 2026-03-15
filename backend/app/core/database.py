from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# Build engine kwargs, skip pool parameters for SQLite
engine_kwargs = {
    "echo": False,
    "future": True,
}

if "sqlite" not in settings.DATABASE_URL.lower():
    # PostgreSQL-specific settings
    engine_kwargs.update({
        "pool_size": 3,
        "max_overflow": 5,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
        "connect_args": {"timeout": 5, "command_timeout": 10},
    })
else:
    # SQLite-specific settings
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
