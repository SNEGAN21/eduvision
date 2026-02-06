# classrooms/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone

from accounts.models import Profile
from .models import ClassSession
from engagement.models import EngagementReport
from .utils import generate_class_report, generate_student_report


# List sessions (teacher vs student)
@login_required
def class_list(request):
    if request.user.profile.role == "teacher":
        sessions = ClassSession.objects.filter(teacher=request.user).order_by("-date")
    else:
        sessions = request.user.enrolled_sessions.all().order_by("-date")
    return render(request, "classrooms/class_list.html", {"sessions": sessions})


# Class detail (teacher-only view)
@login_required
def class_detail(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id, teacher=request.user)

    students = Profile.objects.filter(role="student")
    reports = EngagementReport.objects.filter(session=session)

    student_data, attended_count, total_engagement = [], 0, 0

    for s in students:
        report = reports.filter(student=s.user).first()
        if report:
            attended_count += 1
            total_engagement += report.avg_engagement or 0
        student_data.append({"student": s, "report": report})

    total_students = students.count()
    avg_engagement = (total_engagement / attended_count) if attended_count else 0

    context = {
        "session": session,
        "student_data": student_data,
        "total_students": total_students,
        "attended": attended_count,
        "absent": total_students - attended_count,
        "avg_engagement": round(avg_engagement, 1),
    }
    return render(request, "classrooms/class_detail.html", context)


# Create session (teacher)
@login_required
def create_session(request):
    if request.user.profile.role != "teacher":
        messages.error(request, "Only teachers can create sessions.")
        return redirect("classrooms:class_list")

    if request.method == "POST":
        title = request.POST.get("title")
        subject = request.POST.get("subject")
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        ClassSession.objects.create(
            teacher=request.user,
            title=title,
            subject=subject,
            date=date,
            start_time=start_time,
            end_time=end_time,
        )

        messages.success(request, "Class session created successfully!")
        return redirect("classrooms:class_list")

    return render(request, "classrooms/create_session.html")


# Enroll student into class
@login_required
def enroll(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    if request.user.profile.role == "student":
        session.students.add(request.user)
        messages.success(request, f"You enrolled in {session.title}.")
    return redirect("accounts:dashboard")


# Download full class report (teacher-only)
@login_required
def download_class_report(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id, teacher=request.user)

    students = Profile.objects.filter(role="student")
    reports = EngagementReport.objects.filter(session=session)

    student_data, attended_count, total_engagement = [], 0, 0
    for s in students:
        report = reports.filter(student=s.user).first()
        if report:
            attended_count += 1
            total_engagement += report.avg_engagement or 0
        student_data.append({"student": s, "report": report})

    metrics = {
        "total_students": students.count(),
        "attended": attended_count,
        "absent": students.count() - attended_count,
        "avg_engagement": round(total_engagement / attended_count, 1) if attended_count else 0,
    }

    pdf = generate_class_report(session, student_data, metrics)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="class_report_{session.id}.pdf"'
    return response


# Download single student's report (teacher-only)
@login_required
def download_student_report(request, session_id, student_id):
    session = get_object_or_404(ClassSession, id=session_id, teacher=request.user)
    student = get_object_or_404(Profile, id=student_id, role="student")
    report = EngagementReport.objects.filter(session=session, student=student.user).first()

    pdf = generate_student_report(session, student, report)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="student_report_{student.user.username}_{session.id}.pdf"'
    )
    return response


# Delete session (teacher-only)
@login_required
def delete_session(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id, teacher=request.user)

    if request.method == "POST":
        session.delete()
        messages.success(request, "Class session deleted successfully.")
        return redirect("classrooms:class_list")

    return render(request, "classrooms/delete_session.html", {"session": session})
import io, zipfile
from django.http import HttpResponse
from .utils import generate_student_report  # already exists
from accounts.models import Profile
from engagement.models import EngagementReport

@login_required
def download_all_reports(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id, teacher=request.user)

    # Create in-memory zip
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        students = Profile.objects.filter(role="student")
        for student in students:
            report = EngagementReport.objects.filter(session=session, student=student.user).first()
            if report:
                pdf = generate_student_report(session, student, report)
                filename = f"{student.user.username}_report_{session.id}.pdf"
                zip_file.writestr(filename, pdf)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="class_{session.id}_reports.zip"'
    return response
