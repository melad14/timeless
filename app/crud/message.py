"""Message CRUD operations (MongoDB)."""

from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database

from app.models import Message, message_from_doc
from app.mongo_helpers import parse_object_id
from app.schemas import MessageCreate, MessageUpdate
from app.security import encrypt_message


def get_message_by_id(db: Database, message_id: str) -> Optional[Message]:
    oid = parse_object_id(message_id)
    if oid is None:
        return None
    doc = db.messages.find_one({"_id": oid})
    return message_from_doc(doc)


def create_message(db: Database, message_data: MessageCreate, sender_id: str) -> Message:
    encrypted_content = encrypt_message(message_data.content)
    now = datetime.utcnow()
    doc = {
        "conversation_id": message_data.conversation_id,
        "sender_id": sender_id,
        "content": encrypted_content,
        "content_type": message_data.content_type,
        "is_read": False,
        "is_favorite": False,
        "created_at": now,
        "updated_at": now,
    }
    result = db.messages.insert_one(doc)
    stored = db.messages.find_one({"_id": result.inserted_id})
    return message_from_doc(stored)


def get_conversation_messages(
    db: Database, conversation_id: str, skip: int = 0, limit: int = 50
) -> List[Message]:
    cursor = (
        db.messages.find({"conversation_id": conversation_id})
        .sort("created_at", 1)
        .skip(skip)
        .limit(limit)
    )
    return [message_from_doc(doc) for doc in cursor if doc]


def update_message(db: Database, message_id: str, message_data: MessageUpdate) -> Optional[Message]:
    oid = parse_object_id(message_id)
    if oid is None:
        return None
    doc = db.messages.find_one({"_id": oid})
    if not doc:
        return None

    update_data = message_data.model_dump(exclude_unset=True)
    if "content" in update_data:
        update_data["content"] = encrypt_message(update_data["content"])
    if not update_data:
        return message_from_doc(doc)
    update_data["updated_at"] = datetime.utcnow()

    res = db.messages.find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return message_from_doc(res)


def mark_message_as_read(db: Database, message_id: str) -> Optional[Message]:
    oid = parse_object_id(message_id)
    if oid is None:
        return None

    res = db.messages.find_one_and_update(
        {"_id": oid},
        {"$set": {"is_read": True, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return message_from_doc(res)


def toggle_message_favorite(db: Database, message_id: str) -> Optional[Message]:
    oid = parse_object_id(message_id)
    if oid is None:
        return None

    doc = db.messages.find_one({"_id": oid})
    if not doc:
        return None
    new_value = not bool(doc.get("is_favorite", False))
    res = db.messages.find_one_and_update(
        {"_id": oid},
        {"$set": {"is_favorite": new_value, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return message_from_doc(res)


def delete_message(db: Database, message_id: str, sender_id: str) -> bool:
    oid = parse_object_id(message_id)
    if oid is None:
        return False
    res = db.messages.delete_one({"_id": oid, "sender_id": sender_id})
    return res.deleted_count > 0


def get_favorite_messages(db: Database, user_id: str, skip: int = 0, limit: int = 50) -> List[Message]:
    cursor = (
        db.messages.find({"sender_id": user_id, "is_favorite": True})
        .sort("updated_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return [message_from_doc(doc) for doc in cursor if doc]
