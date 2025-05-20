from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class CoachCreate(UserCreate):
    description: str
    experience_years: int
    profile_photo_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_coach: bool
    description: Optional[str] = None
    experience_years: Optional[int] = None
    profile_photo_url: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    email: EmailStr
    password: str

class CoachList(BaseModel):
    coaches: List[UserResponse] 