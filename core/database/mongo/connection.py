from typing import Annotated
from fastapi.params import Depends
import motor.motor_asyncio
import pymongo
from pymongo.errors import DuplicateKeyError
from .settings import settings


class _Connection:
    def __init__(self):
        """Initialize connection only (without schema)."""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.DATABASE_URL)
        self.db = self.client.get_database(name=settings.DATABASE_NAME)
        self.schema: dict[str, dict] = {}

    async def register_schema(self, schema: dict[str, dict]):
        """Register schema, collections, and indexes."""
        self.schema = schema

        # Register collections dynamically
        for collection_name in schema.keys():
            setattr(self, collection_name, self.db.get_collection(collection_name))

        # Ensure indexes are created
        await self._setup_indexes()

    async def _setup_indexes(self):
        """Ensure indexes are created (idempotent)."""
        for collection_name, rules in self.schema.items():
            collection = getattr(self, collection_name)

            for unique_fields in rules.get("unique", []):
                await self._create_unique_index(collection, unique_fields)

            for index_fields in rules.get("index", []):
                await self._create_index(collection, index_fields)

    async def _create_unique_index(self, collection, fields: list[str]):
        try:
            await collection.create_index(
                [(field, pymongo.ASCENDING) for field in fields], unique=True
            )
        except DuplicateKeyError:
            print(f"WAR: Unique index already exists for {collection.name}: {fields}")

    async def _create_index(self, collection, fields: list[str]):
        try:
            await collection.create_index(
                [(field, pymongo.ASCENDING) for field in fields]
            )
        except DuplicateKeyError:
            print(f"WAR: Index already exists for {collection.name}: {fields}")

    def close(self):
        self.client.close()

    def __getitem__(self, collection_name: str):
        return self.db.get_collection(collection_name)

    def __getattr__(self, item: str):
        return self.db.get_collection(item)


connection = _Connection()

register_schema = connection.register_schema
close_connection = connection.close

ConnectionDependency = Annotated[_Connection, Depends(lambda: connection)]
