"""Message routes implementation for MongoDB-backed conversations."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pymongo.database import Database

from app.models import User, Message
from app.schemas import (
    MessageCreate,
    MessageResponse,
    MessageUpdate,
)
from app.api.dependencies import get_current_active_user
from app.crud.message import (
    get_message_by_id,
    create_message,
    get_conversation_messages,
    update_message,
    mark_message_as_read,
    toggle_message_favorite,
    delete_message,
    get_favorite_messages,
)
from app.crud.conversation import get_conversation_by_id
from app.database import get_db
from app.security import decrypt_message

router = APIRouter(prefix="/messages", tags=["messages"])


def decrypt_message_response(message: Message) -> MessageResponse:
    message_dict = MessageResponse.model_validate(message).model_dump()
    try:
        message_dict["content"] = decrypt_message(message.content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt message content: {exc}"
        )
    return MessageResponse(**message_dict)


@router.post("", response_model=MessageResponse)
def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Send a new message."""
    conversation = get_conversation_by_id(db, message_data.conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    new_message = create_message(db, message_data, current_user.id)
    return decrypt_message_response(new_message)


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get a specific message."""
    message = get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    conversation = get_conversation_by_id(db, message.conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    return decrypt_message_response(message)


@router.put("/{message_id}", response_model=MessageResponse)
def update_message_content(
    message_id: str,
    message_update: MessageUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Update a message."""
    message = get_message_by_id(db, message_id)
    if not message or message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or update not allowed"
        )

    updated_message = update_message(db, message_id, message_update)
    if not updated_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update message"
        )

    return decrypt_message_response(updated_message)


@router.post("/{message_id}/read", response_model=MessageResponse)
def mark_as_read(
    message_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Mark message as read."""
    message = get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    conversation = get_conversation_by_id(db, message.conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    updated_message = mark_message_as_read(db, message_id)
    if not updated_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to mark message as read"
        )

    return decrypt_message_response(updated_message)


@router.post("/{message_id}/favorite", response_model=MessageResponse)
def toggle_favorite(
    message_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Toggle favorite state on a message."""
    message = get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    conversation = get_conversation_by_id(db, message.conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    updated_message = toggle_message_favorite(db, message_id)
    if not updated_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to toggle message favorite"
        )

    return decrypt_message_response(updated_message)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message_endpoint(
    message_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Delete a message."""
    message = get_message_by_id(db, message_id)
    if not message or message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or delete not allowed"
        )

    success = delete_message(db, message_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete message"
        )

    return None


@router.get("/conversation/{conversation_id}", response_model=list[MessageResponse])
def get_conversation_msgs(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get messages from a conversation."""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = get_conversation_messages(db, conversation_id, skip, limit)
    return [decrypt_message_response(message) for message in messages]


@router.get("/user/favorites", response_model=list[MessageResponse])
def get_user_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get user's favorite messages."""
    messages = get_favorite_messages(db, current_user.id, skip, limit)
    return [decrypt_message_response(message) for message in messages]
