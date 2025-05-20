from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from app.core.database import engine, Base
from app.controllers import user_controller, workout_controller, course_controller
from app.controllers.admin import UserAdmin, WorkoutAdmin, CourseAdmin
from app.schemas.user_schemas import TokenRequest
from app.core.auth import create_access_token
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from fastapi import Depends
from app.core.auth import verify_password

app = FastAPI(title="Sport App API")

# Настройка SQLAdmin
admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(WorkoutAdmin)
admin.add_view(CourseAdmin)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(user_controller.router)
app.include_router(user_controller.coach_router)
app.include_router(workout_controller.router)
app.include_router(workout_controller.my_router)
app.include_router(course_controller.router)
app.include_router(course_controller.my_router)

@app.post("/token")
async def login_for_access_token(
    token_request: TokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Получение токена доступа"""
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == token_request.email))
    user = result.scalars().first()
    if not user or not verify_password(token_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Sport App API!"}
