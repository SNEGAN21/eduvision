from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .models import Profile
from classrooms.models import ClassSession
from engagement.models import EngagementReport


# Landing page
def home(request):
    return render(request, "accounts/home.html")


# Teacher login
def teacher_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user and hasattr(user, "profile") and user.profile.role == "teacher":
            login(request, user)
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Only teachers can login here.")

    return render(request, "accounts/teacher_login.html")


# Student login
def student_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user and hasattr(user, "profile") and user.profile.role == "student":
            login(request, user)
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid student credentials.")

    return render(request, "accounts/student_login.html")


# Student signup
def student_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        department = request.POST.get("department")
        year = request.POST.get("year")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, password=password)
            Profile.objects.create(user=user, role="student", department=department, year=year)
            messages.success(request, "Account created! Please login as student.")
            return redirect("accounts:student_login")

    return render(request, "accounts/signup.html")


# Logout
def user_logout(request):
    logout(request)
    return redirect("accounts:home")


# Dashboard (role-based)
@login_required
def dashboard(request):
    profile = request.user.profile
    context = {}

    # ---------------- Teacher Dashboard ----------------
    if profile.role == "teacher":
        sessions = ClassSession.objects.filter(teacher=request.user).order_by("-date")[:5]
        total_sessions = ClassSession.objects.filter(teacher=request.user).count()

        reports = EngagementReport.objects.filter(session__teacher=request.user)
        avg_engagement = reports.aggregate(models.Avg("avg_engagement"))["avg_engagement__avg"] or 0
        total_reports = reports.count()

        # Unique students across teacher’s sessions
        students_enrolled = set()
        for s in ClassSession.objects.filter(teacher=request.user):
            students_enrolled.update(s.students.all())
        total_students = len(students_enrolled)

        # Chart data (last 5 sessions)
        chart_sessions = ClassSession.objects.filter(teacher=request.user).order_by("-date")[:5]
        chart_data = []
        for s in chart_sessions:
            s_reports = EngagementReport.objects.filter(session=s)
            engagement = s_reports.aggregate(models.Avg("avg_engagement"))["avg_engagement__avg"] or 0
            chart_data.append({
                "title": s.title,
                "engagement": round(engagement, 1),
                "students": s.students.count(),
            })

        context.update({
            "is_teacher": True,
            "sessions": sessions,
            "total_sessions": total_sessions,
            "total_students": total_students,
            "avg_engagement": round(avg_engagement, 1),
            "total_reports": total_reports,
            "chart_data": chart_data[::-1],  # oldest → newest
        })
        return render(request, "accounts/teacher_dashboard.html", context)

    # ---------------- Student Dashboard ----------------
    elif profile.role == "student":
        upcoming_classes = ClassSession.objects.filter(
            date__gte=timezone.now().date()
        ).order_by("date")[:5]

        my_reports = EngagementReport.objects.filter(student=request.user).order_by("-created_at")
        avg_engagement = my_reports.aggregate(models.Avg("avg_engagement"))["avg_engagement__avg"] or 0

        context.update({
            "is_teacher": False,
            "upcoming_classes": upcoming_classes,
            "reports": my_reports,
            "avg_engagement": round(avg_engagement, 1),
        })
        return render(request, "accounts/student_dashboard.html", context)

    # ---------------- Invalid ----------------
    else:
        messages.error(request, "Invalid role.")
        return redirect("accounts:home")
