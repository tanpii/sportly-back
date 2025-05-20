from pydantic import BaseModel
from typing import Optional, List
from app.schemas.user_schemas import UserResponse
from app.schemas.workout_schemas import WorkoutWithCoach

class CourseBase(BaseModel):
    title: str
    description: str
    price: Optional[float] = None

class CourseCreate(CourseBase):
    workout_ids: List[int]

class CourseResponse(CourseBase):
    id: int
    coach_id: int
    workouts: List[WorkoutWithCoach]

    class Config:
        from_attributes = True

class CourseWithCoach(CourseResponse):
    coach: UserResponse

    class Config:
        from_attributes = True

class CourseList(BaseModel):
    courses: List[CourseWithCoach]

class CourseListWithCoach(BaseModel):
    courses: List[CourseWithCoach]

class CourseListWithEnrolledUsers(BaseModel):
    courses: List[CourseWithCoach] 