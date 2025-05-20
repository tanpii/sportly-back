from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.controllers.course_controller import CourseController
from app.schemas.course_schemas import CourseCreate, CourseResponse, CourseListWithCoach, CourseListWithEnrolledUsers
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["courses"])
my_router = APIRouter(prefix="/my", tags=["my"])

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание нового курса"""
    controller = CourseController(db)
    return await controller.create_course(course_data, current_user.id)

@router.get("/", response_model=CourseListWithCoach)
async def get_courses(
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех курсов"""
    controller = CourseController(db)
    return await controller.get_all_courses()

@my_router.get("/courses", response_model=CourseListWithEnrolledUsers)
async def get_my_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка курсов текущего пользователя"""
    controller = CourseController(db)
    return await controller.get_my_courses(current_user)

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о курсе"""
    controller = CourseController(db)
    return await controller.get_course(course_id)

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление курса"""
    controller = CourseController(db)
    await controller.delete_course(course_id, current_user.id)
    return {"message": "Course deleted successfully"}

@router.post("/{course_id}/workouts/{workout_id}/remove")
async def remove_workout_from_course(
    course_id: int,
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление тренировки из курса"""
    controller = CourseController(db)
    await controller.remove_workout_from_course(course_id, workout_id, current_user.id)
    return {"message": "Workout removed from course successfully"}

@router.post("/{course_id}/enroll")
async def enroll_to_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Запись на курс"""
    controller = CourseController(db)
    await controller.enroll_to_course(course_id, current_user)
    return {"message": "Successfully enrolled to course"}

@router.post("/{course_id}/unenroll")
async def unenroll_from_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отмена записи на курс"""
    controller = CourseController(db)
    await controller.unenroll_from_course(course_id, current_user)
    return {"message": "Successfully unenrolled from course"} 