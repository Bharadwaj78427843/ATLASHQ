from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import get_settings

# Always source DATABASE_URL from the pydantic-settings singleton so that
# values in .env are honoured consistently (os.getenv bypasses .env loading).
DATABASE_URL = get_settings().DATABASE_URL

# For testing, we might use sqlite. We detect it to set proper engine args.
is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(DATABASE_URL, echo=False, **engine_kwargs)

async_session = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False, 
    autoflush=False
)

async def get_db():
    """FastAPI dependency that yields a transactional AsyncSession.

    On a clean return the session is committed.
    On any exception the session is rolled back before re-raising,
    so partial writes are never silently discarded.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
