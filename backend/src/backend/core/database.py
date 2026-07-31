from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.core.configs import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_size=10,
    max_overflow=20
)

SessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)