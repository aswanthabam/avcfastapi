import motor.motor_asyncio
import pymongo
from pymongo.errors import DuplicateKeyError
from .settings import settings


class Connection:
    _instance = None
    client: motor.motor_asyncio.AsyncIOMotorClient
    db: motor.motor_asyncio.AsyncIOMotorDatabase
    schema: dict[str, dict]

    def __new__(cls):
        if cls._instance is None:
            raise RuntimeError(
                "Connection not initialized. Call setup_db_schema(schema) first."
            )
        return cls._instance

    @classmethod
    async def setup_db_schema(cls, schema: dict[str, dict]):
        """Initialize connection, register collections, and create indexes."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.DATABASE_URL
            )
            cls._instance.db = cls._instance.client.get_database(
                name=settings.DATABASE_NAME
            )
            cls._instance.schema = schema

            # Register collections dynamically
            for collection_name in schema.keys():
                setattr(
                    cls._instance,
                    collection_name,
                    cls._instance.db.get_collection(collection_name),
                )

        # Always ensure indexes are created (idempotent in Mongo)
        for collection_name, rules in schema.items():
            collection = getattr(cls._instance, collection_name)

            for unique_fields in rules.get("unique", []):
                await cls._create_unique_index(collection, unique_fields)

            for index_fields in rules.get("index", []):
                await cls._create_index(collection, index_fields)

        return cls._instance

    @staticmethod
    async def _create_unique_index(collection, fields: list[str]):
        try:
            await collection.create_index(
                [(field, pymongo.ASCENDING) for field in fields], unique=True
            )
        except DuplicateKeyError:
            print("WAR: Unique index already exists.")

    @staticmethod
    async def _create_index(collection, fields: list[str]):
        try:
            await collection.create_index(
                [(field, pymongo.ASCENDING) for field in fields]
            )
        except DuplicateKeyError:
            print("WAR: Index already exists.")

    def close(self):
        self.client.close()

    def __getitem__(self, collection_name: str):
        return self.db.get_collection(collection_name)

    def __getattr__(self, item: str):
        return self.db.get_collection(item)
