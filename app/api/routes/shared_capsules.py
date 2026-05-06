from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from app.database import get_db
from app.crud.time_capsule import get_time_capsule_by_id, attach_capsule_user
from app.security import decrypt_message
from app.schemas import TimeCapsuleDetailResponse

router = APIRouter(prefix="/shared-capsules", tags=["shared-capsules"])

@router.get("/{capsule_id}", response_model=TimeCapsuleDetailResponse)
def get_shared_capsule(
    capsule_id: str,
    db: Database = Depends(get_db)
):
    """
    Get a specific time capsule by ID without authentication.
    Only returns content if the capsule is_opened is True.
    """
    capsule = get_time_capsule_by_id(db, capsule_id)
    if not capsule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time capsule not found"
        )

    if not capsule.is_opened:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This time capsule is not yet open. Please check back later."
        )

    capsule = attach_capsule_user(db, capsule)
    
    try:
        decrypted_content = decrypt_message(capsule.content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt capsule content: {exc}"
        )

    capsule_dict = TimeCapsuleDetailResponse.model_validate(capsule).model_dump()
    capsule_dict['content'] = decrypted_content

    return TimeCapsuleDetailResponse(**capsule_dict)
