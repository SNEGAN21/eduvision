from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),   # 👈 this is the "accounts:home"
    path("login/", views.teacher_login, name="teacher_login"),
    path("student-login/", views.student_login, name="student_login"),
    path("signup/", views.student_signup, name="student_signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.user_logout, name="logout"),
    
]
