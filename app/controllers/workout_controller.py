from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from app.models.workout import Workout
from app.models.user import User
from app.schemas.workout_schemas import WorkoutCreate, WorkoutListWithCoach, WorkoutListWithEnrolledUsers, WorkoutResponse, WorkoutList
from fastapi import HTTPException, status, APIRouter, Depends
from app.core.database import get_db
from app.core.auth import get_current_user, get_current_coach

router = APIRouter(prefix="/workouts", tags=["workouts"])
my_router = APIRouter(prefix="/my/workouts", tags=["my-workouts"])

class WorkoutController:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_workout(self, workout_data: WorkoutCreate, coach_id: int) -> Workout:
        """Создание новой тренировки"""
        datetime_without_tz = workout_data.datetime.replace(tzinfo=None)
        
        new_workout = Workout(
            title=workout_data.title,
            description=workout_data.description,
            datetime=datetime_without_tz,
            address=workout_data.address,
            price=workout_data.price,
            sport_type=workout_data.sport_type,
            coach_id=coach_id
        )
        self.session.add(new_workout)
        await self.session.commit()
        await self.session.refresh(new_workout)
        return new_workout

    async def get_all_workouts(self, search: str = None) -> WorkoutListWithCoach:
        """Получение списка всех тренировок"""
        query = (
            select(Workout)
            .options(joinedload(Workout.coach))
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Workout.title.ilike(search_term),
                    Workout.sport_type.ilike(search_term)
                )
            )
        
        query = query.order_by(Workout.datetime)
        
        result = await self.session.execute(query)
        workouts = result.scalars().all()
        return WorkoutListWithCoach(workouts=workouts)

    async def delete_workout(self, workout_id: int, coach_id: int) -> None:
        """Удаление тренировки"""
        result = await self.session.execute(
            select(Workout).where(
                Workout.id == workout_id,
                Workout.coach_id == coach_id
            )
        )
        workout = result.scalars().first()
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренировка не найдена или у вас нет прав на её удаление"
            )

        await self.session.delete(workout)
        await self.session.commit()

    async def enroll_to_workout(self, workout_id: int, user: User) -> Workout:
        """Запись на тренировку"""
        if user.is_coach:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тренеры не могут записываться на тренировки"
            )

        result = await self.session.execute(
            select(Workout).where(Workout.id == workout_id)
        )
        workout = result.scalars().first()
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренировка не найдена"
            )

        if workout in user.enrolled_workouts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже записаны на эту тренировку"
            )

        user.enrolled_workouts.append(workout)
        await self.session.commit()
        await self.session.refresh(workout)
        return workout

    async def unenroll_from_workout(self, workout_id: int, user: User) -> None:
        """Отмена записи на тренировку"""
        if user.is_coach:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Тренеры не могут отписываться от тренировок"
            )

        result = await self.session.execute(
            select(Workout).where(Workout.id == workout_id)
        )
        workout = result.scalars().first()
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренировка не найдена"
            )

        if workout not in user.enrolled_workouts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы не записаны на эту тренировку"
            )

        user.enrolled_workouts.remove(workout)
        await self.session.commit()

    async def get_my_workouts(self, user: User) -> WorkoutListWithEnrolledUsers:
        """Получение списка тренировок пользователя"""
        if user.is_coach:
            query = (
                select(Workout)
                .options(
                    joinedload(Workout.coach),
                    joinedload(Workout.enrolled_users)
                )
                .where(Workout.coach_id == user.id)
            )
        else:
            query = (
                select(Workout)
                .options(joinedload(Workout.coach))
                .join(Workout.enrolled_users)
                .where(User.id == user.id)
            )

        result = await self.session.execute(query)
        workouts = result.unique().scalars().all()
        return WorkoutListWithEnrolledUsers(workouts=workouts)

# Роуты для всех тренировок
@router.post("/", response_model=WorkoutResponse)
async def create_workout(
    workout_data: WorkoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_coach)
):
    controller = WorkoutController(db)
    return await controller.create_workout(workout_data, current_user)

@router.get("/", response_model=WorkoutList)
async def get_all_workouts(
    db: AsyncSession = Depends(get_db)
):
    controller = WorkoutController(db)
    return await controller.get_all_workouts()

@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    db: AsyncSession = Depends(get_db)
):
    controller = WorkoutController(db)
    return await controller.get_workout(workout_id)

# Роуты для личных тренировок
@my_router.get("/", response_model=WorkoutListWithEnrolledUsers)
async def get_my_workouts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    controller = WorkoutController(db)
    return await controller.get_my_workouts(current_user)

@my_router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_my_workout(
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    controller = WorkoutController(db)
    return await controller.get_my_workout(workout_id, current_user) 