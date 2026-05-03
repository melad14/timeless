"""Conversation routes implementation for MongoDB-backed conversations."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pymongo.database import Database

from app.models import User
from app.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationUpdate,
)
from app.api.dependencies import get_current_active_user
from app.crud.conversation import (
    get_conversation_by_id,
    create_conversation,
    get_user_conversations,
    add_member_to_conversation,
    remove_member_from_conversation,
    update_conversation,
    delete_conversation,
    attach_conversation_members,
)
from app.crud.user import get_user_by_id
from app.database import get_db

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse)
def create_new_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Create a new conversation."""
    for member_id in conversation_data.member_ids:
        if get_user_by_id(db, member_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {member_id} not found"
            )

    new_conversation = create_conversation(db, conversation_data, current_user.id)
    return ConversationResponse.model_validate(new_conversation)


@router.get("", response_model=list[ConversationResponse])
def get_user_convs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get all conversations for current user."""
    conversations = get_user_conversations(db, current_user.id, skip, limit)
    return [ConversationResponse.model_validate(conv) for conv in conversations]


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get conversation details."""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    conversation = attach_conversation_members(db, conversation)
    if conversation.members is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation members not found"
        )

    return ConversationDetailResponse.model_validate(conversation)


@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation_info(
    conversation_id: str,
    conversation_update: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Update conversation information."""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    updated_conversation = update_conversation(db, conversation_id, conversation_update)
    if not updated_conversation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update conversation"
        )

    return ConversationResponse.model_validate(updated_conversation)


@router.post("/{conversation_id}/members/{user_id}", response_model=ConversationResponse)
def add_member(
    conversation_id: str,
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Add member to conversation."""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    if get_user_by_id(db, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    updated_conversation = add_member_to_conversation(db, conversation_id, user_id)
    if not updated_conversation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add member"
        )

    return ConversationResponse.model_validate(updated_conversation)


@router.delete("/{conversation_id}/members/{user_id}", response_model=ConversationResponse)
def remove_member(
    conversation_id: str,
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Remove member from conversation."""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    updated_conversation = remove_member_from_conversation(db, conversation_id, user_id)
    if not updated_conversation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove member"
        )

    return ConversationResponse.model_validate(updated_conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Delete a conversation."""
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or current_user.id not in conversation.member_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    success = delete_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete conversation"
        )

    return None
