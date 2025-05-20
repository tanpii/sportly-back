from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.schemas.base_schemas import UserBase, UserResponse
from app.schemas.workout_schemas import WorkoutWithCoach
from app.schemas.course_schemas import CourseWithCoach

class UserCreate(UserBase):
    password: str

class CoachCreate(UserCreate):
    description: str
    experience_years: int
    profile_photo_url: Optional[str] = None

class CoachResponse(UserResponse):
    workouts: List[WorkoutWithCoach]
    courses: List[CourseWithCoach]

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