from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user_schemas import UserResponse

class WorkoutBase(BaseModel):
    title: str
    description: str
    datetime: datetime
    address: str
    price: Optional[float] = None
    sport_type: str

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutResponse(WorkoutBase):
    id: int
    coach_id: int
    is_course_part: bool

    class Config:
        from_attributes = True

class WorkoutWithCoach(WorkoutResponse):
    coach: UserResponse

    class Config:
        from_attributes = True

class WorkoutList(BaseModel):
    workouts: List[WorkoutWithCoach]

class WorkoutListWithCoach(BaseModel):
    workouts: List[WorkoutWithCoach]

class WorkoutListWithEnrolledUsers(BaseModel):
    workouts: List[WorkoutWithCoach] 