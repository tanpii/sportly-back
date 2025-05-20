from sqladmin import ModelView
from app.models.user import User
from app.models.workout import Workout
from app.models.course import Course
from app.models.base import Base

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.first_name, User.last_name, User.is_coach, User.phone_number]
    column_searchable_list = [User.email, User.first_name, User.last_name]
    column_sortable_list = [User.id, User.email, User.is_coach]
    form_columns = [User.email, User.first_name, User.last_name, User.middle_name, User.phone_number, User.is_coach, User.description, User.experience_years]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class WorkoutAdmin(ModelView, model=Workout):
    column_list = [Workout.id, Workout.title, Workout.coach_id, Workout.datetime, Workout.sport_type]
    column_searchable_list = [Workout.title]
    column_sortable_list = [Workout.id, Workout.datetime, Workout.sport_type]
    form_columns = [Workout.title, Workout.description, Workout.coach_id, Workout.datetime, Workout.address, Workout.price, Workout.sport_type]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

class CourseAdmin(ModelView, model=Course):
    column_list = [Course.id, Course.title, Course.coach_id, Course.price]
    column_searchable_list = [Course.title]
    column_sortable_list = [Course.id, Course.price]
    form_columns = [Course.title, Course.description, Course.coach_id, Course.price]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True 