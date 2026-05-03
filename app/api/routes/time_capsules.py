"""Time Capsule routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pymongo.database import Database
from app.database import get_db

from app.models import User
from app.schemas import (
    TimeCapsuleCreate,
    TimeCapsuleResponse,
    TimeCapsuleUpdate,
    TimeCapsuleDetailResponse
)
from app.api.dependencies import get_current_active_user
from app.crud.time_capsule import (
    get_time_capsule_by_id,
    create_time_capsule,
    get_user_time_capsules,
    update_time_capsule,
    open_time_capsule,
    delete_time_capsule,
    get_opened_time_capsules,
    get_pending_time_capsules_for_user,
    get_pending_time_capsules,
    attach_capsule_user,
)
from app.security import decrypt_message
from app.mongo_helpers import utc_naive
from datetime import datetime

router = APIRouter(prefix="/time-capsules", tags=["time-capsules"])


@router.post("", response_model=TimeCapsuleResponse)
def create_time_capsule_endpoint(
    capsule_data: TimeCapsuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
):
    """Create a new time capsule"""
    if utc_naive(capsule_data.open_date) <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Open date must be in the future"
        )

    new_capsule = create_time_capsule(db, capsule_data, current_user.id)
    return TimeCapsuleResponse.model_validate(new_capsule)


@router.get("", response_model=list[TimeCapsuleResponse])
def get_my_time_capsules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
):
    """Get current user's time capsules"""
    capsules = get_user_time_capsules(db, current_user.id, skip, limit)
    return [TimeCapsuleResponse.model_validate(capsule) for capsule in capsules]


@router.get("/pending", response_model=list[TimeCapsuleResponse])
def get_my_pending_capsules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
):
    """Get current user's pending (not opened) time capsules"""
    capsules = get_pending_time_capsules_for_user(db, current_user.id, skip, limit)
    return [TimeCapsuleResponse.model_validate(capsule) for capsule in capsules]


@router.get("/opened", response_model=list[TimeCapsuleDetailResponse])
def get_my_opened_capsules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
):
    """Get current user's opened time capsules with decrypted content"""
    capsules = get_opened_time_capsules(db, current_user.id, skip, limit)
    result = []
    for capsule in capsules:
        try:
            decrypted_content = decrypt_message(capsule.content)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to decrypt opened capsule content: {exc}"
            )
        capsule_dict = TimeCapsuleDetailResponse.model_validate(capsule).model_dump()
        capsule_dict['content'] = decrypted_content
        result.append(TimeCapsuleDetailResponse(**capsule_dict))
    return result


@router.get("/{capsule_id}", response_model=TimeCapsuleDetailResponse)
def get_time_capsule(
    capsule_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
):
    """Get a specific time capsule by ID"""
    capsule = get_time_capsule_by_id(db, capsule_id)
    if not capsule or capsule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time capsule not found"
        )

    capsule = attach_capsule_user(db, capsule)
    if not capsule.user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time capsule not found"
        )

    capsule_dict = TimeCapsuleDetailResponse.model_validate(capsule).model_dump()

    if capsule.is_opened:
        try:
            capsule_dict['content'] = decrypt_message(capsule.content)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to decrypt capsule content: {exc}"
            )

    return TimeCapsuleDetailResponse(**capsule_dict)


@router.put("/{capsule_id}", response_model=TimeCapsuleResponse)
def update_time_capsule_endpoint(
    capsule_id: str,
    capsule_data: TimeCapsuleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
):
    """Update a time capsule (only if not opened and before open date)"""
    capsule = get_time_capsule_by_id(db, capsule_id)
    if not capsule or capsule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time capsule not found"
        )

    updated_capsule = update_time_capsule(db, capsule_id, capsule_data)
    if not updated_capsule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update opened capsule or open date has passed"
        )

    return TimeCapsuleResponse.model_validate(updated_capsule)


@router.post("/{capsule_id}/open", response_model=TimeCapsuleDetailResponse)
def open_time_capsule_endpoint(
    capsule_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
):
    """Open a time capsule (only when open date has arrived)"""
    capsule = get_time_capsule_by_id(db, capsule_id)
    if not capsule or capsule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time capsule not found"
        )

    opened_capsule = open_time_capsule(db, capsule_id)
    if not opened_capsule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot open capsule yet or already opened"
        )

    opened_capsule = attach_capsule_user(db, opened_capsule)
    if not opened_capsule.user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time capsule not found"
        )

    try:
        decrypted_content = decrypt_message(opened_capsule.content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt opened capsule content: {exc}"
        )

    capsule_dict = TimeCapsuleDetailResponse.model_validate(opened_capsule).model_dump()
    capsule_dict['content'] = decrypted_content

    return TimeCapsuleDetailResponse(**capsule_dict)


@router.delete("/{capsule_id}", response_model=dict)
def delete_time_capsule_endpoint(
    capsule_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db)
):
    """Delete a time capsule (only if not opened)"""
    success = delete_time_capsule(db, capsule_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time capsule not found or already opened"
        )

    return {"message": "Time capsule deleted successfully"}


@router.post("/check-ready", response_model=dict)
def check_ready_capsules(db: Database = Depends(get_db)):
    """Check and open time capsules that are ready (for scheduled tasks)"""
    current_time = datetime.utcnow()
    ready_capsules = get_pending_time_capsules(db, current_time)

    opened_count = 0
    for capsule in ready_capsules:
        open_time_capsule(db, capsule.id)
        opened_count += 1

    return {"message": f"Opened {opened_count} time capsules"}
