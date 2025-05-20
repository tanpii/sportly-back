from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from app.models.base import Base

# Таблица связи для тренировок и пользователей
workout_enrollments = Table(
    "workout_enrollments",
    Base.metadata,
    Column("workout_id", Integer, ForeignKey("workouts.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    datetime = Column(DateTime)
    address = Column(String)
    price = Column(Float, nullable=True)
    sport_type = Column(String)
    coach_id = Column(Integer, ForeignKey("users.id"))
    is_course_part = Column(Boolean, default=False)

    # Отношения
    coach = relationship("User", back_populates="workouts")
    enrolled_users = relationship(
        "User",
        secondary=workout_enrollments,
        back_populates="enrolled_workouts"
    )
    courses = relationship("Course", secondary="course_workouts", back_populates="workouts") 