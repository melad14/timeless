"""MongoDB connection and database access."""

from typing import Generator

from pymongo import MongoClient
from pymongo.database import Database

from app.config import get_settings

_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(settings.mongodb_uri)
    return _client


def get_database() -> Database:
    settings = get_settings()
    return get_mongo_client()[settings.mongodb_db_name]


def ensure_indexes() -> None:
    db = get_database()
    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True)
    db.time_capsules.create_index([("user_id", 1), ("created_at", -1)])
    db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
    db.messages.create_index([("sender_id", 1), ("is_favorite", 1)])
    db.conversations.create_index([("member_ids", 1), ("updated_at", -1)])


def get_db() -> Generator[Database, None, None]:
    """FastAPI dependency: yields Mongo database handle."""
    yield get_database()


def reset_client_for_tests() -> None:
    """Close client between tests."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
