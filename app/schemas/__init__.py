"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, EmailStr, Field
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
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


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
    id: int
    user_id: int
    is_opened: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TimeCapsuleDetailResponse(TimeCapsuleResponse):
    """Detailed time capsule response with user info"""
    user: UserResponse
