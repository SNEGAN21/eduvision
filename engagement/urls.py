from django.urls import path
from . import views

app_name = "engagement"

urlpatterns = [
    path("record/<int:session_id>/", views.record_engagement, name="record"),
    path("ingest/<int:session_id>/", views.ingest_engagement, name="ingest"),
    path("finish/<int:session_id>/", views.finish_engagement, name="finish"),
 
     path("reports/", views.report_list, name="report_list"),  
     
     path("teacher-report/<int:session_id>/<int:student_id>/", 
     views.teacher_student_report, 
     name="teacher_student_report"),
      path("report/<int:report_id>/", views.student_report_detail, name="student_report_detail"),

path("student-report/<int:report_id>/", views.student_report_detail, name="student_report"),  # alias



]
