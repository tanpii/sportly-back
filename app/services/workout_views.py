from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.controllers.workout_controller import WorkoutController
from app.schemas.workout_schemas import WorkoutCreate, WorkoutResponse, WorkoutListWithCoach, WorkoutListWithEnrolledUsers
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/workouts", tags=["workouts"])
my_router = APIRouter(prefix="/my", tags=["my"])

@router.post("/", response_model=WorkoutResponse)
async def create_workout(
    workout_data: WorkoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание новой тренировки"""
    controller = WorkoutController(db)
    return await controller.create_workout(workout_data, current_user.id)

@router.get("/", response_model=WorkoutListWithCoach)
async def get_workouts(
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех тренировок"""
    controller = WorkoutController(db)
    return await controller.get_all_workouts()

@my_router.get("/workouts", response_model=WorkoutListWithEnrolledUsers)
async def get_my_workouts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка тренировок текущего пользователя"""
    controller = WorkoutController(db)
    return await controller.get_my_workouts(current_user)

@router.delete("/{workout_id}")
async def delete_workout(
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление тренировки"""
    controller = WorkoutController(db)
    await controller.delete_workout(workout_id, current_user.id)
    return {"message": "Workout deleted successfully"}

@router.post("/{workout_id}/enroll")
async def enroll_to_workout(
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Запись на тренировку"""
    controller = WorkoutController(db)
    await controller.enroll_to_workout(workout_id, current_user)
    return {"message": "Successfully enrolled to workout"}

@router.post("/{workout_id}/unenroll")
async def unenroll_from_workout(
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отмена записи на тренировку"""
    controller = WorkoutController(db)
    await controller.unenroll_from_workout(workout_id, current_user)
    return {"message": "Successfully unenrolled from workout"} 