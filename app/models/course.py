from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from app.models.base import Base

# Таблица связи для курсов и тренировок
course_workouts = Table(
    "course_workouts",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("workout_id", Integer, ForeignKey("workouts.id"))
)

# Таблица связи для курсов и пользователей
course_enrollments = Table(
    "course_enrollments",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    price = Column(Float, nullable=True)
    coach_id = Column(Integer, ForeignKey("users.id"))

    # Отношения
    coach = relationship("User", back_populates="courses")
    workouts = relationship("Workout", secondary=course_workouts, back_populates="courses")
    enrolled_users = relationship("User", secondary=course_enrollments, back_populates="enrolled_courses") 