from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from app.models.course import Course
from app.models.workout import Workout
from app.models.user import User
from app.schemas.course_schemas import CourseCreate, CourseListWithCoach, CourseListWithEnrolledUsers, CourseResponse, CourseList
from fastapi import HTTPException, status, APIRouter, Depends
from app.core.database import get_db
from app.core.auth import get_current_user, get_current_coach

router = APIRouter(prefix="/courses", tags=["courses"])
my_router = APIRouter(prefix="/my/courses", tags=["my-courses"])

class CourseController:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_course(self, course_data: CourseCreate, coach_id: int) -> Course:
        """Создание нового курса"""
        async with self.session.begin():
            result = await self.session.execute(
                select(Workout).where(
                    Workout.id.in_(course_data.workout_ids),
                    Workout.coach_id == coach_id
                )
            )
            workouts = result.scalars().all()
            
            if len(workouts) != len(course_data.workout_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Некоторые тренировки не найдены или не принадлежат вам"
                )
            
            for workout in workouts:
                workout.is_course_part = True
            
            new_course = Course(
                title=course_data.title,
                description=course_data.description,
                price=course_data.price,
                coach_id=coach_id,
                workouts=workouts
            )
            
            self.session.add(new_course)
            await self.session.flush()
            await self.session.refresh(new_course)
            await self.session.refresh(new_course, ['workouts'])
            
            return new_course

    async def get_all_courses(self, search: str = None) -> CourseListWithCoach:
        """Получение списка всех курсов"""
        async with self.session.begin():
            query = (
                select(Course)
                .options(joinedload(Course.coach), joinedload(Course.workouts))
            )
            
            if search:
                search_term = f"%{search}%"
                query = query.join(Course.workouts).where(
                    or_(
                        Course.title.ilike(search_term),
                        Workout.sport_type.ilike(search_term)
                    )
                )
            
            result = await self.session.execute(query)
            courses = result.unique().scalars().all()
            return CourseListWithCoach(courses=courses)

    async def get_course(self, course_id: int) -> Course:
        """Получение информации о курсе"""
        async with self.session.begin():
            result = await self.session.execute(
                select(Course)
                .options(joinedload(Course.coach), joinedload(Course.workouts))
                .where(Course.id == course_id)
            )
            course = result.scalars().first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Курс не найден"
                )
            return course

    async def delete_course(self, course_id: int, coach_id: int) -> None:
        """Удаление курса"""
        async with self.session.begin():
            result = await self.session.execute(
                select(Course).where(
                    Course.id == course_id,
                    Course.coach_id == coach_id
                )
            )
            course = result.scalars().first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Курс не найден или у вас нет прав на его удаление"
                )

            await self.session.delete(course)

    async def remove_workout_from_course(self, course_id: int, workout_id: int, coach_id: int) -> None:
        """Удаление тренировки из курса"""
        async with self.session.begin():
            result = await self.session.execute(
                select(Course).where(
                    Course.id == course_id,
                    Course.coach_id == coach_id
                )
            )
            course = result.scalars().first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Курс не найден или у вас нет прав на его изменение"
                )

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
                    detail="Тренировка не найдена или не принадлежит вам"
                )
            
            course.workouts.remove(workout)
            
            result = await self.session.execute(
                select(Course).join(Course.workouts).where(Workout.id == workout_id)
            )
            remaining_courses = result.scalars().all()
            
            if not remaining_courses:
                workout.is_course_part = False

    async def enroll_to_course(self, course_id: int, user: User) -> Course:
        """Запись на курс"""
        async with self.session.begin():
            if user.is_coach:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Тренеры не могут записываться на курсы"
                )

            result = await self.session.execute(
                select(User)
                .options(joinedload(User.enrolled_courses))
                .where(User.id == user.id)
            )
            user = result.scalars().first()

            result = await self.session.execute(
                select(Course).where(Course.id == course_id)
            )
            course = result.scalars().first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Курс не найден"
                )

            if course in user.enrolled_courses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Вы уже записаны на этот курс"
                )

            user.enrolled_courses.append(course)
            await self.session.flush()
            await self.session.refresh(course)
            return course

    async def unenroll_from_course(self, course_id: int, user: User) -> None:
        """Отмена записи на курс"""
        async with self.session.begin():
            if user.is_coach:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Тренеры не могут отписываться от курсов"
                )

            result = await self.session.execute(
                select(User)
                .options(joinedload(User.enrolled_courses))
                .where(User.id == user.id)
            )
            user = result.scalars().first()

            result = await self.session.execute(
                select(Course).where(Course.id == course_id)
            )
            course = result.scalars().first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Курс не найден"
                )

            if course not in user.enrolled_courses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Вы не записаны на этот курс"
                )

            user.enrolled_courses.remove(course)

    async def get_my_courses(self, user: User) -> CourseListWithEnrolledUsers:
        """Получение списка курсов пользователя"""
        async with self.session.begin():
            if user.is_coach:
                query = (
                    select(Course)
                    .options(
                        joinedload(Course.coach),
                        joinedload(Course.workouts),
                        joinedload(Course.enrolled_users)
                    )
                    .where(Course.coach_id == user.id)
                )
            else:
                query = (
                    select(Course)
                    .options(
                        joinedload(Course.coach),
                        joinedload(Course.workouts)
                    )
                    .join(Course.enrolled_users)
                    .where(User.id == user.id)
                )

            result = await self.session.execute(query)
            courses = result.unique().scalars().all()
            return CourseListWithEnrolledUsers(courses=courses)

    async def get_my_course(self, course_id: int, user: User) -> Course:
        """Получение информации о курсе пользователя"""
        if user.is_coach:
            query = (
                select(Course)
                .options(
                    joinedload(Course.coach),
                    joinedload(Course.workouts),
                    joinedload(Course.enrolled_users)
                )
                .where(
                    Course.id == course_id,
                    Course.coach_id == user.id
                )
            )
        else:
            query = (
                select(Course)
                .options(
                    joinedload(Course.coach),
                    joinedload(Course.workouts)
                )
                .join(Course.enrolled_users)
                .where(
                    Course.id == course_id,
                    User.id == user.id
                )
            )

        result = await self.session.execute(query)
        course = result.scalars().first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Курс не найден или у вас нет к нему доступа"
            )
        return course

# Роуты для всех курсов
@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_coach)
):
    async with db as session:
        controller = CourseController(session)
        return await controller.create_course(course_data, current_user.id)

@router.get("/", response_model=CourseList)
async def get_all_courses(
    db: AsyncSession = Depends(get_db)
):
    async with db as session:
        controller = CourseController(session)
        return await controller.get_all_courses()

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    async with db as session:
        controller = CourseController(session)
        return await controller.get_course(course_id)

# Роуты для личных курсов
@my_router.get("/", response_model=CourseListWithEnrolledUsers)
async def get_my_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    async with db as session:
        controller = CourseController(session)
        return await controller.get_my_courses(current_user)

@my_router.get("/{course_id}", response_model=CourseResponse)
async def get_my_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    async with db as session:
        controller = CourseController(session)
        return await controller.get_my_course(course_id, current_user)

@router.post("/{course_id}/enroll")
async def enroll_to_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    async with db as session:
        controller = CourseController(session)
        await controller.enroll_to_course(course_id, current_user)
        return {"message": "Successfully enrolled to course"}

@router.post("/{course_id}/unenroll")
async def unenroll_from_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    async with db as session:
        controller = CourseController(session)
        await controller.unenroll_from_course(course_id, current_user)
        return {"message": "Successfully unenrolled from course"}