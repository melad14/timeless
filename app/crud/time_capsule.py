"""Time Capsule CRUD operations (MongoDB)."""

from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo.database import Database
from pymongo import ReturnDocument

from app.models import TimeCapsule, User, time_capsule_from_doc, user_from_doc
from app.mongo_helpers import parse_object_id, utc_naive
from app.schemas import TimeCapsuleCreate, TimeCapsuleUpdate
from app.security import encrypt_message
from app.utils.email import send_capsule_opened_email


def attach_capsule_user(db: Database, capsule: TimeCapsule) -> TimeCapsule:
    if capsule.user is None:
        udoc = db.users.find_one({"_id": ObjectId(capsule.user_id)})
        capsule.user = user_from_doc(udoc)
    return capsule


def get_time_capsule_by_id(db: Database, capsule_id: str) -> Optional[TimeCapsule]:
    oid = parse_object_id(capsule_id)
    if oid is None:
        return None
    doc = db.time_capsules.find_one({"_id": oid})
    return time_capsule_from_doc(doc)


def create_time_capsule(
    db: Database, capsule_data: TimeCapsuleCreate, user_id: str
) -> TimeCapsule:
    encrypted_content = encrypt_message(capsule_data.content)
    now = datetime.utcnow()
    doc = {
        "user_id": user_id,
        "title": capsule_data.title,
        "content": encrypted_content,
        "content_type": capsule_data.content_type,
        "open_date": utc_naive(capsule_data.open_date),
        "recipients": capsule_data.recipients,
        "is_opened": False,
        "created_at": now,
        "updated_at": now,
    }
    result = db.time_capsules.insert_one(doc)
    stored = db.time_capsules.find_one({"_id": result.inserted_id})
    return time_capsule_from_doc(stored)


def get_user_time_capsules(
    db: Database, user_id: str, skip: int = 0, limit: int = 50
) -> List[TimeCapsule]:
    cursor = (
        db.time_capsules.find({"user_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return [time_capsule_from_doc(d) for d in cursor if d]


def get_pending_time_capsules(
    db: Database, current_time: datetime
) -> List[TimeCapsule]:
    cursor = db.time_capsules.find(
        {"open_date": {"$lte": current_time}, "is_opened": False}
    )
    return [time_capsule_from_doc(d) for d in cursor if d]


def update_time_capsule(
    db: Database, capsule_id: str, capsule_data: TimeCapsuleUpdate
) -> Optional[TimeCapsule]:
    oid = parse_object_id(capsule_id)
    if oid is None:
        return None
    doc = db.time_capsules.find_one({"_id": oid})
    if not doc or doc.get("is_opened"):
        return None
    if utc_naive(doc["open_date"]) <= datetime.utcnow():
        return None

    update_data = capsule_data.model_dump(exclude_unset=True)
    if "content" in update_data:
        update_data["content"] = encrypt_message(update_data["content"])
    if "open_date" in update_data:
        update_data["open_date"] = utc_naive(update_data["open_date"])
    update_data["updated_at"] = datetime.utcnow()

    res = db.time_capsules.find_one_and_update(
        {"_id": oid, "is_opened": False},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return time_capsule_from_doc(res)


def open_time_capsule(db: Database, capsule_id: str) -> Optional[TimeCapsule]:
    oid = parse_object_id(capsule_id)
    if oid is None:
        return None
    doc = db.time_capsules.find_one({"_id": oid})
    if not doc or doc.get("is_opened"):
        return None
    if utc_naive(doc["open_date"]) > datetime.utcnow():
        return None

    res = db.time_capsules.find_one_and_update(
        {"_id": oid, "is_opened": False},
        {"$set": {"is_opened": True, "updated_at": datetime.utcnow()}},
        return_document=ReturnDocument.AFTER,
    )
    
    if res and res.get("recipients"):
        send_capsule_opened_email(res["recipients"], res["title"], str(res["_id"]))
        
    return time_capsule_from_doc(res)


def delete_time_capsule(
    db: Database, capsule_id: str, user_id: str
) -> bool:
    oid = parse_object_id(capsule_id)
    if oid is None:
        return False
    res = db.time_capsules.delete_one(
        {"_id": oid, "user_id": user_id, "is_opened": False}
    )
    return res.deleted_count > 0


def get_opened_time_capsules(
    db: Database, user_id: str, skip: int = 0, limit: int = 50
) -> List[TimeCapsule]:
    cursor = (
        db.time_capsules.find({"user_id": user_id, "is_opened": True})
        .sort("open_date", -1)
        .skip(skip)
        .limit(limit)
    )
    out: List[TimeCapsule] = []
    for d in cursor:
        cap = time_capsule_from_doc(d)
        if cap:
            udoc = db.users.find_one({"_id": ObjectId(cap.user_id)})
            cap.user = user_from_doc(udoc)
            out.append(cap)
    return out


def get_pending_time_capsules_for_user(
    db: Database, user_id: str, skip: int = 0, limit: int = 50
) -> List[TimeCapsule]:
    cursor = (
        db.time_capsules.find({"user_id": user_id, "is_opened": False})
        .sort("open_date", 1)
        .skip(skip)
        .limit(limit)
    )
    return [time_capsule_from_doc(d) for d in cursor if d]
