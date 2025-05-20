from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from app.core.database import engine, Base
from app.controllers import user_controller, workout_controller, course_controller
from app.controllers.admin import UserAdmin, WorkoutAdmin, CourseAdmin

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

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Sport App API!"}
