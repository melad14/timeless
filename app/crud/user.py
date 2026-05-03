"""User CRUD operations (MongoDB)."""

from datetime import datetime
from typing import Optional

from pymongo import ReturnDocument
from pymongo.database import Database

from app.models import User, user_from_doc
from app.mongo_helpers import parse_object_id
from app.security import hash_password
from app.schemas import UserCreate, UserUpdate


def get_user_by_id(db: Database, user_id: str) -> Optional[User]:
    oid = parse_object_id(user_id)
    if oid is None:
        return None
    doc = db.users.find_one({"_id": oid})
    return user_from_doc(doc)


def get_user_by_email(db: Database, email: str) -> Optional[User]:
    doc = db.users.find_one({"email": email})
    return user_from_doc(doc)


def get_user_by_username(db: Database, username: str) -> Optional[User]:
    doc = db.users.find_one({"username": username})
    return user_from_doc(doc)


def create_user(db: Database, user: UserCreate) -> User:
    hashed_password = hash_password(user.password)
    now = datetime.utcnow()
    doc = {
        "email": user.email,
        "username": user.username,
        "phone_number": user.phone_number,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_verified": False,
        "created_at": now,
        "updated_at": now,
    }
    result = db.users.insert_one(doc)
    stored = db.users.find_one({"_id": result.inserted_id})
    return user_from_doc(stored)


def update_user(db: Database, user_id: str, user_data: UserUpdate) -> Optional[User]:
    oid = parse_object_id(user_id)
    if oid is None:
        return None
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        doc = db.users.find_one({"_id": oid})
        return user_from_doc(doc)
    update_data["updated_at"] = datetime.utcnow()
    res = db.users.find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return user_from_doc(res)


def authenticate_user(db: Database, email: str, password: str) -> Optional[User]:
    from app.security import verify_password

    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def deactivate_user(db: Database, user_id: str) -> bool:
    oid = parse_object_id(user_id)
    if oid is None:
        return False
    res = db.users.update_one(
        {"_id": oid},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}},
    )
    return res.modified_count > 0 or res.matched_count > 0
