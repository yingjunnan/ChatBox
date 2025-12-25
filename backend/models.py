from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    email: Optional[EmailStr]
    avatar_url: Optional[str]
    created_at: str

class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    password_hash: str
    display_name: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    created_at: str
    updated_at: str
