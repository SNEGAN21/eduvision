from django.db import models
# engagement/models.py

from django.db import models
from django.contrib.auth.models import User
from classrooms.models import ClassSession

from django.db import models
from django.contrib.auth.models import User
from classrooms.models import ClassSession

class EngagementReport(models.Model):
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    avg_engagement = models.FloatField(default=0)
    attention = models.FloatField(default=0)
    dominant_emotion = models.CharField(max_length=50, default="Neutral")
    neutral = models.IntegerField(default=0)
    happy = models.IntegerField(default=0)
    sad = models.IntegerField(default=0)
    angry = models.IntegerField(default=0)
    surprise = models.IntegerField(default=0)
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def duration_minutes(self):
        if self.joined_at and self.left_at:
            return int((self.left_at - self.joined_at).total_seconds() // 60)
        return 0
