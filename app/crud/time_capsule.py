"""Time Capsule CRUD operations"""

from sqlalchemy.orm import Session
from app.models import TimeCapsule
from app.schemas import TimeCapsuleCreate, TimeCapsuleUpdate
from app.security import encrypt_message, decrypt_message
from datetime import datetime
from typing import List, Optional


def get_time_capsule_by_id(db: Session, capsule_id: int) -> Optional[TimeCapsule]:
    """Get time capsule by ID"""
    return db.query(TimeCapsule).filter(TimeCapsule.id == capsule_id).first()


def create_time_capsule(db: Session, capsule_data: TimeCapsuleCreate, user_id: int) -> TimeCapsule:
    """Create new time capsule"""
    encrypted_content = encrypt_message(capsule_data.content)

    db_capsule = TimeCapsule(
        user_id=user_id,
        title=capsule_data.title,
        content=encrypted_content,
        content_type=capsule_data.content_type,
        open_date=capsule_data.open_date
    )
    db.add(db_capsule)
    db.commit()
    db.refresh(db_capsule)
    return db_capsule


def get_user_time_capsules(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[TimeCapsule]:
    """Get all time capsules for a user"""
    return db.query(TimeCapsule).filter(TimeCapsule.user_id == user_id).offset(skip).limit(limit).all()


def get_pending_time_capsules(db: Session, current_time: datetime) -> List[TimeCapsule]:
    """Get time capsules that are ready to be opened (past open_date and not opened yet)"""
    return db.query(TimeCapsule).filter(
        TimeCapsule.open_date <= current_time,
        TimeCapsule.is_opened == False
    ).all()


def update_time_capsule(db: Session, capsule_id: int, capsule_data: TimeCapsuleUpdate) -> Optional[TimeCapsule]:
    """Update time capsule (only if not opened and before open date)"""
    db_capsule = db.query(TimeCapsule).filter(TimeCapsule.id == capsule_id).first()
    if not db_capsule or db_capsule.is_opened:
        return None

    # Check if open date has passed
    if db_capsule.open_date <= datetime.utcnow():
        return None

    update_data = capsule_data.model_dump(exclude_unset=True)
    if 'content' in update_data:
        update_data['content'] = encrypt_message(update_data['content'])

    for field, value in update_data.items():
        setattr(db_capsule, field, value)

    db.commit()
    db.refresh(db_capsule)
    return db_capsule


def open_time_capsule(db: Session, capsule_id: int) -> Optional[TimeCapsule]:
    """Mark time capsule as opened"""
    db_capsule = db.query(TimeCapsule).filter(TimeCapsule.id == capsule_id).first()
    if not db_capsule or db_capsule.is_opened:
        return None

    # Check if it's time to open
    if db_capsule.open_date > datetime.utcnow():
        return None

    db_capsule.is_opened = True
    db.commit()
    db.refresh(db_capsule)
    return db_capsule


def delete_time_capsule(db: Session, capsule_id: int, user_id: int) -> bool:
    """Delete a time capsule (only if not opened)"""
    db_capsule = db.query(TimeCapsule).filter(
        TimeCapsule.id == capsule_id,
        TimeCapsule.user_id == user_id,
        TimeCapsule.is_opened == False
    ).first()
    if not db_capsule:
        return False

    db.delete(db_capsule)
    db.commit()
    return True


def get_opened_time_capsules(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[TimeCapsule]:
    """Get user's opened time capsules"""
    return db.query(TimeCapsule).filter(
        TimeCapsule.user_id == user_id,
        TimeCapsule.is_opened == True
    ).offset(skip).limit(limit).all()


def get_pending_time_capsules_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[TimeCapsule]:
    """Get user's pending (not opened) time capsules"""
    return db.query(TimeCapsule).filter(
        TimeCapsule.user_id == user_id,
        TimeCapsule.is_opened == False
    ).offset(skip).limit(limit).all()