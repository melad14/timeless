"""Domain models (MongoDB documents mapped to Python types)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from bson import ObjectId


@dataclass
class User:
    id: str
    email: str
    username: str
    phone_number: Optional[str]
    hashed_password: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class TimeCapsule:
    id: str
    user_id: str
    title: str
    content: str
    content_type: str
    open_date: datetime
    is_opened: bool
    created_at: datetime
    updated_at: datetime
    is_notified: bool = False
    recipients: list[str] = field(default_factory=list)
    recipients_phones: list[str] = field(default_factory=list)
    user: Optional[User] = None


@dataclass
class Message:
    id: str
    conversation_id: str
    sender_id: str
    content: str
    content_type: str
    is_read: bool
    is_favorite: bool
    scheduled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


@dataclass
class Conversation:
    id: str
    title: str
    member_ids: list[str]
    owner_id: str
    created_at: datetime
    updated_at: datetime
    members: Optional[list[User]] = None


def user_from_doc(doc: Optional[dict[str, Any]]) -> Optional[User]:
    if not doc:
        return None
    return User(
        id=str(doc["_id"]),
        email=doc["email"],
        username=doc["username"],
        phone_number=doc.get("phone_number"),
        hashed_password=doc["hashed_password"],
        is_active=bool(doc.get("is_active", True)),
        is_verified=bool(doc.get("is_verified", False)),
        is_admin=bool(doc.get("is_admin", False)),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


def time_capsule_from_doc(
    doc: Optional[dict[str, Any]],
    *,
    user: Optional[User] = None,
) -> Optional[TimeCapsule]:
    if not doc:
        return None
    uid = doc["user_id"]
    if isinstance(uid, ObjectId):
        uid = str(uid)
    return TimeCapsule(
        id=str(doc["_id"]),
        user_id=str(uid),
        title=doc["title"],
        content=doc["content"],
        content_type=doc["content_type"],
        open_date=doc["open_date"],
        is_opened=bool(doc.get("is_opened", False)),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        is_notified=bool(doc.get("is_notified", False)),
        recipients=doc.get("recipients", []),
        recipients_phones=doc.get("recipients_phones", []),
        user=user,
    )


def message_from_doc(doc: Optional[dict[str, Any]]) -> Optional[Message]:
    if not doc:
        return None
    return Message(
        id=str(doc["_id"]),
        conversation_id=str(doc["conversation_id"]),
        sender_id=str(doc["sender_id"]),
        content=doc["content"],
        content_type=doc["content_type"],
        is_read=bool(doc.get("is_read", False)),
        is_favorite=bool(doc.get("is_favorite", False)),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        metadata=doc.get("metadata", {}),
        scheduled_at=doc.get("scheduled_at"),
    )


def conversation_from_doc(doc: Optional[dict[str, Any]]) -> Optional[Conversation]:
    if not doc:
        return None
    return Conversation(
        id=str(doc["_id"]),
        title=doc["title"],
        member_ids=[str(mid) for mid in doc.get("member_ids", [])],
        owner_id=str(doc.get("owner_id")),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        members=None,
    )
