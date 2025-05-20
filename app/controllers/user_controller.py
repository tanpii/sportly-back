from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user_schemas import UserCreate, CoachList, TokenRequest, UserResponse
from app.core.auth import get_password_hash, create_access_token, verify_password
from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy.orm import joinedload
from datetime import timedelta
from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])
coach_router = APIRouter(prefix="/coaches", tags=["coaches"])

class UserController:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже зарегистрирован"
            )

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            middle_name=user_data.middle_name,
            phone_number=user_data.phone_number,
            hashed_password=hashed_password,
            is_coach=False
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def create_coach(self, user_data: UserCreate) -> User:
        """Создание нового тренера"""
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже зарегистрирован"
            )

        hashed_password = get_password_hash(user_data.password)
        new_coach = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            middle_name=user_data.middle_name,
            phone_number=user_data.phone_number,
            hashed_password=hashed_password,
            is_coach=True
        )
        self.session.add(new_coach)
        await self.session.commit()
        await self.session.refresh(new_coach)
        return new_coach

    async def login(self, token_request: TokenRequest) -> dict:
        """Аутентификация пользователя"""
        user = await self.get_user_by_email(token_request.email)
        if not user or not verify_password(token_request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_user_by_email(self, email: str) -> User:
        """Получение пользователя по email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User:
        """Получение пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_all_coaches(self) -> CoachList:
        """Получение списка всех тренеров"""
        result = await self.session.execute(
            select(User).where(User.is_coach == True)
        )
        coaches = result.scalars().all()
        return CoachList(coaches=coaches)

    async def get_coach_with_workouts(self, coach_id: int) -> User:
        """Получение тренера с его тренировками и курсами"""
        result = await self.session.execute(
            select(User)
            .options(
                joinedload(User.workouts),
                joinedload(User.courses)
            )
            .where(User.id == coach_id, User.is_coach == True)
        )
        coach = result.unique().scalars().first()
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тренер не найден"
            )
        return coach

# Роуты для пользователей
@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.create_user(user_data)

@router.post("/login")
async def login(
    token_request: TokenRequest,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.login(token_request)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user

# Роуты для тренеров
@coach_router.post("/", response_model=UserResponse)
async def create_coach(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.create_coach(user_data)

@coach_router.get("/", response_model=CoachList)
async def get_all_coaches(
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.get_all_coaches()

@coach_router.get("/{coach_id}", response_model=UserResponse)
async def get_coach_with_workouts(
    coach_id: int,
    db: AsyncSession = Depends(get_db)
):
    controller = UserController(db)
    return await controller.get_coach_with_workouts(coach_id) 