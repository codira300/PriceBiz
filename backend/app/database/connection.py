from datetime import timezone

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import MONGODB_URL, MONGODB_DATABASE_NAME


client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(
            MONGODB_URL,
            tz_aware=True,
            tzinfo=timezone.utc,
        )
    return client


class _DatabaseProxy:
    """Lazy proxy so `database.refresh_tokens` works like before."""

    def __getattr__(self, name: str):
        return get_client()[MONGODB_DATABASE_NAME][name]

    async def list_collection_names(self, *args, **kwargs):
        return await get_client()[
            MONGODB_DATABASE_NAME
        ].list_collection_names(*args, **kwargs)

    async def create_collection(self, *args, **kwargs):
        return await get_client()[
            MONGODB_DATABASE_NAME
        ].create_collection(*args, **kwargs)

    async def command(self, *args, **kwargs):
        return await get_client()[
            MONGODB_DATABASE_NAME
        ].command(*args, **kwargs)


database = _DatabaseProxy()