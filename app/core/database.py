from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


engine: AsyncEngine | None = None
session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db(url: str, echo: bool = False) -> None:
    global engine, session_factory

    engine = create_async_engine(url, echo=echo, pool_size=5, max_overflow=10)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def close_db() -> None:
    global engine, session_factory

    if engine:
        await engine.dispose()

    engine = None
    session_factory = None


def get_session() -> AsyncSession:
    if session_factory is None:
        raise RuntimeError("Database not initialized")

    return session_factory()
