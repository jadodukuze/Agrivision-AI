"""Pydantic schemas for API input and output."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    preferred_language: str = Field(default="en", pattern="^(en|rw)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    role: str
    preferred_language: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ReviewRequest(BaseModel):
    assessment: str = Field(min_length=5, max_length=5000)
    recommended_next_steps: str | None = Field(default=None, max_length=5000)


class CaseResponse(BaseModel):
    id: str
    farmer_id: int
    crop_name: str
    location: str | None
    description: str | None
    status: str
    created_at: datetime
    has_image: bool = True


class StaffCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    role: str = Field(pattern="^(expert|admin)$")
