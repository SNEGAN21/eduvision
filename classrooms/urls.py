from django.urls import path
from . import views

app_name = "classrooms"

urlpatterns = [
    path("", views.class_list, name="class_list"),
    path("<int:session_id>/", views.class_detail, name="class_detail"),
    path("", views.class_list, name="class_list"),
    path("<int:session_id>/", views.class_detail, name="class_detail"),
    path("create/", views.create_session, name="create_session"),
    path("<int:session_id>/enroll/", views.enroll, name="enroll"),
    path("<int:session_id>/download/", views.download_class_report, name="download_class_report"),
    path("<int:session_id>/student/<int:student_id>/download/", views.download_student_report, name="download_student_report"),
    path("<int:session_id>/delete/", views.delete_session, name="delete_session"),
    path("<int:session_id>/download-all/", views.download_all_reports, name="download_all_reports"),  # ✅ new




]
