"""Conversation CRUD operations (MongoDB)."""

from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database

from app.models import Conversation, User, user_from_doc
from app.mongo_helpers import parse_object_id
from app.schemas import ConversationCreate, ConversationUpdate


def get_conversation_by_id(db: Database, conversation_id: str) -> Optional[Conversation]:
    oid = parse_object_id(conversation_id)
    if oid is None:
        return None
    doc = db.conversations.find_one({"_id": oid})
    return conversation_from_doc(doc)


def create_conversation(db: Database, conversation_data: ConversationCreate, owner_id: str) -> Conversation:
    members = list({owner_id, *conversation_data.member_ids})
    now = datetime.utcnow()
    doc = {
        "title": conversation_data.title,
        "member_ids": members,
        "owner_id": owner_id,
        "created_at": now,
        "updated_at": now,
    }
    result = db.conversations.insert_one(doc)
    stored = db.conversations.find_one({"_id": result.inserted_id})
    return conversation_from_doc(stored)


def get_user_conversations(
    db: Database, user_id: str, skip: int = 0, limit: int = 50
) -> List[Conversation]:
    cursor = (
        db.conversations.find({"member_ids": user_id})
        .sort("updated_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return [conversation_from_doc(doc) for doc in cursor if doc]


def update_conversation(db: Database, conversation_id: str, conversation_data: ConversationUpdate) -> Optional[Conversation]:
    oid = parse_object_id(conversation_id)
    if oid is None:
        return None
    doc = db.conversations.find_one({"_id": oid})
    if not doc:
        return None

    update_data = conversation_data.model_dump(exclude_unset=True)
    if not update_data:
        return conversation_from_doc(doc)
    update_data["updated_at"] = datetime.utcnow()

    res = db.conversations.find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return conversation_from_doc(res)


def add_member_to_conversation(db: Database, conversation_id: str, user_id: str) -> Optional[Conversation]:
    oid = parse_object_id(conversation_id)
    if oid is None:
        return None

    res = db.conversations.find_one_and_update(
        {"_id": oid},
        {"$addToSet": {"member_ids": user_id}, "$set": {"updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return conversation_from_doc(res)


def remove_member_from_conversation(db: Database, conversation_id: str, user_id: str) -> Optional[Conversation]:
    oid = parse_object_id(conversation_id)
    if oid is None:
        return None

    res = db.conversations.find_one_and_update(
        {"_id": oid},
        {"$pull": {"member_ids": user_id}, "$set": {"updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    return conversation_from_doc(res)


def delete_conversation(db: Database, conversation_id: str, user_id: str) -> bool:
    oid = parse_object_id(conversation_id)
    if oid is None:
        return False
    res = db.conversations.delete_one({"_id": oid, "member_ids": user_id})
    return res.deleted_count > 0


def attach_conversation_members(db: Database, conversation: Conversation) -> Conversation:
    if conversation.members is None:
        users = list(db.users.find({"_id": {"$in": [ObjectId(uid) for uid in conversation.member_ids]}}))
        conversation.members = [user_from_doc(doc) for doc in users if doc]
    return conversation


def conversation_from_doc(doc: Optional[dict]) -> Optional[Conversation]:
    if not doc:
        return None
    return Conversation(
        id=str(doc["_id"]),
        title=doc["title"],
        member_ids=doc.get("member_ids", []),
        owner_id=doc.get("owner_id"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        members=None,
    )
