from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.controllers.user_controller import UserController
from app.schemas.user_schemas import UserCreate, UserResponse, Token, TokenRequest, CoachList, CoachCreate, CoachResponse
from app.config.s3_config import upload_profile_photo
from app.utils.auth import get_current_user, get_current_coach, get_password_hash, create_access_token
from app.models.user import User
from datetime import timedelta
from pydantic import EmailStr

ACCESS_TOKEN_EXPIRE_DAYS = 7

router = APIRouter(prefix="/users", tags=["users"])
coach_router = APIRouter(prefix="/coaches", tags=["coaches"])

@router.post("/", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    controller = UserController(db)
    return await controller.create_user(user_data)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user

@coach_router.post("/", response_model=Token)
async def register_coach(
    email: EmailStr = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: str = Form(None),
    description: str = Form(...),
    experience_years: int = Form(...),
    profile_photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового тренера"""
    # Проверяем, не зарегистрирован ли уже email
    result = await db.execute(
        select(User).where(User.email == email)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Загружаем фото профиля
    profile_photo_url = await upload_profile_photo(profile_photo)
    if not profile_photo_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to upload profile photo"
        )

    # Создаем нового тренера
    hashed_password = get_password_hash(password)
    new_coach = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        hashed_password=hashed_password,
        is_coach=True,
        description=description,
        experience_years=experience_years,
        profile_photo_url=profile_photo_url
    )
    db.add(new_coach)
    await db.commit()
    await db.refresh(new_coach)

    # Создаем токен доступа
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": new_coach.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(
    token_request: TokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Вход в систему"""
    controller = UserController(db)
    return await controller.login(token_request)

@coach_router.get("/", response_model=CoachList)
async def get_coaches(
    db: AsyncSession = Depends(get_db)
):
    """Получение списка всех тренеров"""
    controller = UserController(db)
    return await controller.get_all_coaches()

@coach_router.get("/{coach_id}", response_model=CoachResponse)
async def get_coach(
    coach_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о тренере"""
    controller = UserController(db)
    return await controller.get_coach_with_workouts(coach_id)

@router.post("/profile/photo")
async def upload_photo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Загрузка фото профиля"""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    url = await upload_profile_photo(file)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload file")
    
    return {"url": url} 