from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import EngagementReport

@login_required
def report_list(request):
    if request.user.profile.role == "teacher":
        reports = EngagementReport.objects.all()
    else:
        reports = EngagementReport.objects.filter(student=request.user)
    return render(request, "engagement/report_list.html", {"reports": reports})
import cv2, time
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import EngagementReport
from classrooms.models import ClassSession
from core.emotion_model import EmotionModel
from core.engagement import engagement_score

from django.utils import timezone
from .models import EngagementReport

@login_required
def record_engagement(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    
    report, created = EngagementReport.objects.get_or_create(
        session=session,
        student=request.user,
        defaults={"joined_at": timezone.now()}
    )
    if not created and not report.joined_at:
        report.joined_at = timezone.now()
        report.save()

    return render(request, "engagement/capture.html", {"session": session})


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import EngagementReport
@login_required
def student_report_detail(request, report_id):
    report = get_object_or_404(EngagementReport, id=report_id, student=request.user)
    session = report.session

    attention = report.avg_engagement or 0
    distracted = 100 - attention

    context = {
        "session": session,
        "duration" :(
    (report.left_at - report.joined_at).seconds // 60
    if report.joined_at and report.left_at else 0
),
        "engagement": report.avg_engagement or 0,
        "attention": attention,
        "distracted": distracted,
        "mood": getattr(report, "dominant_emotion", "Neutral"),
        "emotions": {
            "neutral": getattr(report, "neutral", 0),
            "happy": getattr(report, "happy", 0),
            "surprise": getattr(report, "surprise", 0),
            "sad": getattr(report, "sad", 0),
            "angry": getattr(report, "angry", 0),
        }
    }
    return render(request, "engagement/student_report.html", context)




import cv2
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models

from classrooms.models import ClassSession
from accounts.models import Profile
from .models import EngagementReport
from core.emotion_model import EmotionModel   # your CNN

# Temporary store per-user stats in DB
from django.contrib.sessions.models import Session as DjangoSession


@login_required
def record_engagement(request, session_id):
    """Show webcam page"""
    session = get_object_or_404(ClassSession, id=session_id)
    return render(request, "engagement/capture.html", {"session": session})
# engagement/views.py (only the ingest view shown/updated)
import cv2, numpy as np
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from core.emotion_model import EmotionModel
from core.mediapipe_utils import face_landmarks_rgb, eye_aspect_ratio, gaze_center_score, head_yaw_penalty
from core.engagement import engagement_score

# Load model once at import to avoid cold start per frame
_EMO = EmotionModel()
@login_required
def finish_engagement(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    report, _ = EngagementReport.objects.get_or_create(session=session, student=request.user)

    stats = request.session.get("eng_stats_v2")

    if stats and stats["scores"]:
        frames = len(stats["scores"])
        report.avg_engagement = sum(stats["scores"]) / frames
        report.attention = (sum(stats["scores"]) / frames) * 100  # proxy %

        emotions = stats.get("emotions", {})
        report.neutral = emotions.get("neutral", 0)
        report.happy = emotions.get("happy", 0)
        report.sad = emotions.get("sad", 0)
        report.angry = emotions.get("angry", 0)
        report.surprise = emotions.get("surprise", 0)
        report.dominant_emotion = max(emotions, key=emotions.get, default="Neutral")
    else:
        report.avg_engagement = 0
        report.attention = 0

    if not report.joined_at:
        report.joined_at = timezone.now()
    report.left_at = timezone.now()
    report.save()

    if "eng_stats_v2" in request.session:
        del request.session["eng_stats_v2"]

    return redirect("engagement:student_report_detail", report.id)



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from accounts.models import Profile
from classrooms.models import ClassSession
from .models import EngagementReport

@login_required
def teacher_student_report(request, session_id, student_id):
    # Ensure only teacher of this session can view
    session = get_object_or_404(ClassSession, id=session_id, teacher=request.user)
    student = get_object_or_404(Profile, id=student_id, role="student")

    report = EngagementReport.objects.filter(session=session, student=student.user).first()
    if not report:
        messages.error(request, "No report found for this student.")
        return redirect("classrooms:class_detail", session_id=session.id)

    # Attendance time (real join-leave if you add later)
    duration = (
    (report.left_at - report.joined_at).seconds // 60
    if report.joined_at and report.left_at else 0
)


    attention = report.avg_engagement or 0
    distracted = 100 - attention

    context = {
        "session": session,
        "student": student,
        "duration": duration,
        "engagement": report.avg_engagement or 0,
        "attention": attention,
        "distracted": distracted,
        "mood": getattr(report, "dominant_emotion", "Neutral"),
        "emotions": {
            "neutral": getattr(report, "neutral", 0),
            "happy": getattr(report, "happy", 0),
            "surprise": getattr(report, "surprise", 0),
            "sad": getattr(report, "sad", 0),
            "angry": getattr(report, "angry", 0),
        },
    }
    return render(request, "engagement/student_report.html", context)

@login_required
def ingest_engagement(request, session_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)

    file = request.FILES.get("frame")
    if not file:
        return JsonResponse({"error": "No frame"}, status=400)

    # Decode uploaded frame
    arr = np.frombuffer(file.read(), np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        return JsonResponse({"error": "Decode failed"}, status=400)

    # Convert to RGB
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    # ✅ Emotion from your trained CNN
    emo_label, emo_prob = _EMO.predict_emotion(bgr)  # <-- your model

    # ✅ Landmarks (EAR, gaze, yaw)
    landmarks, w, h = face_landmarks_rgb(rgb)
    if landmarks is not None:
        ear = eye_aspect_ratio(landmarks, w, h)
        gaze = gaze_center_score(landmarks, w, h)
        yaw = head_yaw_penalty(landmarks)
    else:
        # No face → penalize
        ear, gaze, yaw = 0.12, 0.0, 0.0

    # ✅ Engagement score (weighted formula)
    score = (0.4 * gaze) + (0.3 * emo_prob) + (0.2 * ear) + (0.1 * yaw)

    # ✅ Rolling average & emotion frequency
    stats = request.session.get("eng_stats_v2", {"scores": [], "emotions": {}})

    stats["scores"].append(float(score))
    if len(stats["scores"]) > 30:   # keep last 30 frames (~30s)
        stats["scores"].pop(0)

    stats["emotions"][emo_label] = stats["emotions"].get(emo_label, 0) + 1

    request.session["eng_stats_v2"] = stats
    request.session.modified = True

    return JsonResponse({
        "emotion": emo_label,
        "emotion_prob": round(float(emo_prob), 3),
        "score": round(float(score), 2)
    })
