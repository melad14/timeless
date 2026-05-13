"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import List, Optional


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=255)
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=255)
    phone_number: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class UserDetailResponse(UserResponse):
    """Detailed user response with relationships"""
    pass


# Authentication Schemas
class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None


# Time Capsule Schemas
class TimeCapsuleBase(BaseModel):
    """Base time capsule schema"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)  # Encrypted content
    content_type: str = Field(..., pattern="^(text|image|video)$")
    open_date: datetime = Field(..., description="Date and time when the capsule should be opened")
    recipients: List[EmailStr] = Field(default_factory=list, description="List of recipient emails")


class TimeCapsuleCreate(TimeCapsuleBase):
    """Time capsule creation schema"""
    pass


class TimeCapsuleUpdate(BaseModel):
    """Time capsule update schema (only before open date)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[str] = Field(None, pattern="^(text|image|video)$")


class TimeCapsuleResponse(TimeCapsuleBase):
    """Time capsule response schema"""
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    user_id: str
    is_opened: bool
    is_notified: bool
    created_at: datetime
    updated_at: datetime


class TimeCapsuleDetailResponse(TimeCapsuleResponse):
    """Detailed time capsule response with user info"""
    user: UserResponse


# Message Schemas
class MessageBase(BaseModel):
    """Base message schema"""
    conversation_id: str
    content: str = Field(..., min_length=1)
    content_type: str = Field(..., pattern="^(text|image|video)$")
    metadata: dict = Field(default_factory=dict)


class MessageCreate(MessageBase):
    """Message creation schema"""
    scheduled_at: Optional[datetime] = None


class MessageUpdate(BaseModel):
    """Message update schema"""
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[str] = Field(None, pattern="^(text|image|video)$")


class MessageResponse(MessageBase):
    """Message response schema"""
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    sender_id: str
    is_read: bool
    is_favorite: bool
    scheduled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# Conversation Schemas
class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: str = Field(..., min_length=1, max_length=255)
    member_ids: list[str] = Field(default_factory=list)


class ConversationCreate(ConversationBase):
    """Conversation creation schema"""
    pass


class ConversationUpdate(BaseModel):
    """Conversation update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)


class ConversationResponse(ConversationBase):
    """Conversation response schema"""
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    """Detailed conversation response with member info"""
    members: list[UserResponse] = []
