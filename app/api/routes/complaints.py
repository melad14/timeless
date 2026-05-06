from fastapi import APIRouter, Depends, Query
from pymongo.database import Database
from app.database import get_db
from app.models import Message, message_from_doc, User
from app.schemas import MessageResponse
from app.security import decrypt_message
from typing import List

from app.api.dependencies import get_admin_user

router = APIRouter(prefix="/admin/complaints", tags=["admin-complaints"])

def decrypt_msg(msg_doc) -> MessageResponse:
    msg = message_from_doc(msg_doc)
    msg_dict = MessageResponse.model_validate(msg).model_dump()
    try:
        msg_dict["content"] = decrypt_message(msg.content)
    except:
        msg_dict["content"] = "[Decryption Failed]"
    return MessageResponse(**msg_dict)

@router.get("", response_model=List[MessageResponse])
def get_all_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Database = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Get all messages that are marked as complaints or suggestions in metadata.
    This is an admin-only view.
    """
    cursor = (
        db.messages.find({"metadata.type": {"$in": ["complaint", "suggestion"]}})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    
    return [decrypt_msg(doc) for doc in cursor]
