from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/postgres"
)

async def database_exists(db_name: str) -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ),
            {"db_name": db_name},
        )
        return result.scalar() is not None


