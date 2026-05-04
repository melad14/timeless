"""Seed script for the Timeless backend database.

This script inserts sample users, conversations, messages, and time capsules
into the configured MongoDB database. Use --reset to drop existing collections
and seed a clean dataset.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from typing import Any

from app.config import get_settings
from app.database import ensure_indexes, get_database
from app.security.encryption import encrypt_message
from app.security.password import hash_password


def reset_database(db: Any) -> None:
    print("Resetting MongoDB collections...")
    for collection_name in ["users", "conversations", "messages", "time_capsules"]:
        db[collection_name].drop()
    ensure_indexes()
    print("Database reset complete.")


def create_user_doc(email: str, username: str, password: str, phone_number: str | None = None) -> dict[str, Any]:
    now = datetime.utcnow()
    return {
        "email": email,
        "username": username,
        "phone_number": phone_number,
        "hashed_password": hash_password(password),
        "is_active": True,
        "is_verified": True,
        "created_at": now,
        "updated_at": now,
    }


def seed_users(db: Any) -> list[dict[str, Any]]:
    print("Seeding users...")
    users = [
        create_user_doc("alice@example.com", "alice", "Password123!", "+966500000001"),
        create_user_doc("bob@example.com", "bob", "Password123!", "+966500000002"),
        create_user_doc("carol@example.com", "carol", "Password123!", "+966500000003"),
    ]
    seeded = []
    for user in users:
        db.users.update_one(
            {"email": user["email"]},
            {"$setOnInsert": user},
            upsert=True,
        )
        stored = db.users.find_one({"email": user["email"]})
        seeded.append(stored)
    print(f"Inserted or reused {len(seeded)} users.")
    return seeded


def seed_conversations(db: Any, users: list[dict[str, Any]]) -> list[dict[str, Any]]:
    print("Seeding conversations...")
    alice_id = str(users[0]["_id"])
    bob_id = str(users[1]["_id"])
    carol_id = str(users[2]["_id"])

    conversations = [
        {
            "title": "Alice & Bob chat",
            "member_ids": [alice_id, bob_id],
            "owner_id": alice_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        {
            "title": "Team Timeless",
            "member_ids": [alice_id, bob_id, carol_id],
            "owner_id": bob_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
    ]
    seeded = []
    for conv in conversations:
        db.conversations.update_one(
            {"title": conv["title"], "owner_id": conv["owner_id"]},
            {"$setOnInsert": conv},
            upsert=True,
        )
        stored = db.conversations.find_one({"title": conv["title"], "owner_id": conv["owner_id"]})
        seeded.append(stored)
    print(f"Inserted or reused {len(seeded)} conversations.")
    return seeded


def create_time_capsule_doc(user_id: str, title: str, content: str, open_date: datetime) -> dict[str, Any]:
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "title": title,
        "content": encrypt_message(content),
        "content_type": "text",
        "open_date": open_date,
        "is_opened": False,
        "created_at": now,
        "updated_at": now,
    }


def seed_time_capsules(db: Any, users: list[dict[str, Any]]) -> list[dict[str, Any]]:
    print("Seeding time capsules...")
    alice_id = str(users[0]["_id"])
    bob_id = str(users[1]["_id"])

    capsules = [
        create_time_capsule_doc(
            alice_id,
            "Secret memory",
            "This capsule opens tomorrow. Keep it safe.",
            datetime.utcnow() + timedelta(days=1),
        ),
        create_time_capsule_doc(
            bob_id,
            "Open now",
            "This time capsule is ready to read.",
            datetime.utcnow() - timedelta(days=1),
        ),
    ]
    seeded = []
    for cap in capsules:
        db.time_capsules.insert_one(cap)
        seeded.append(cap)
    print(f"Inserted {len(seeded)} time capsules.")
    return seeded


def create_message_doc(conversation_id: str, sender_id: str, content: str, content_type: str = "text", is_favorite: bool = False, is_read: bool = False) -> dict[str, Any]:
    now = datetime.utcnow()
    return {
        "conversation_id": conversation_id,
        "sender_id": sender_id,
        "content": encrypt_message(content),
        "content_type": content_type,
        "is_read": is_read,
        "is_favorite": is_favorite,
        "created_at": now,
        "updated_at": now,
    }


def seed_messages(db: Any, conversations: list[dict[str, Any]], users: list[dict[str, Any]]) -> None:
    print("Seeding messages...")
    alice_id = str(users[0]["_id"])
    bob_id = str(users[1]["_id"])
    carol_id = str(users[2]["_id"])

    messages = [
        create_message_doc(conversations[0]["_id"], alice_id, "Hello Bob, ready for the launch?", is_read=True),
        create_message_doc(conversations[0]["_id"], bob_id, "Yes Alice, everything looks good.", is_favorite=True),
        create_message_doc(conversations[1]["_id"], carol_id, "Hey team, let's sync on the next milestone.", is_read=False),
        create_message_doc(conversations[1]["_id"], alice_id, "Sounds good! I'll share the doc soon.", is_read=False),
    ]
    for msg in messages:
        db.messages.insert_one(msg)
    print(f"Inserted {len(messages)} messages.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the Timeless MongoDB database with sample data.")
    parser.add_argument("--reset", action="store_true", help="Drop existing collections before seeding")
    args = parser.parse_args()

    settings = get_settings()
    db = get_database()

    print(f"Using MongoDB: {settings.mongodb_uri}/{settings.mongodb_db_name}")
    if args.reset:
        reset_database(db)
    else:
        ensure_indexes()

    users = seed_users(db)
    conversations = seed_conversations(db, users)
    seed_time_capsules(db, users)
    seed_messages(db, conversations, users)

    print("\nSeed data finished successfully.")


if __name__ == "__main__":
    main()
