from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_coach: bool
    description: Optional[str] = None
    experience_years: Optional[int] = None
    profile_photo_url: Optional[str] = None

    class Config:
        from_attributes = True 