from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.workout import workout_enrollments

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    hashed_password = Column(String)
    is_coach = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)
    profile_photo_url = Column(String, nullable=True)

    # Отношения
    workouts = relationship("Workout", back_populates="coach")
    courses = relationship("Course", back_populates="coach")
    enrolled_workouts = relationship(
        "Workout",
        secondary=workout_enrollments,
        back_populates="enrolled_users"
    )
    enrolled_courses = relationship(
        "Course",
        secondary="course_enrollments",
        back_populates="enrolled_users"
    ) 