from app.database.connection import client, database
from app.database.collections import COLLECTIONS
from app.database.indexes import initialize_indexes


async def initialize_database():
    existing_collections = await database.list_collection_names()

    for collection in COLLECTIONS:
        if collection not in existing_collections:
            await database.create_collection(collection)

    await initialize_indexes()


__all__ = [
    "client",
    "database",
    "initialize_database",
]