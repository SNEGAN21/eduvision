from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class ClassSession(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teaching_sessions")
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100, null=True, blank=True)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Add this Many-to-Many field
    students = models.ManyToManyField(User, related_name="enrolled_sessions", blank=True)

    def duration_minutes(self):
        if self.start_time and self.end_time:
            from datetime import datetime, timedelta
            start = datetime.combine(self.date, self.start_time)
            end = datetime.combine(self.date, self.end_time)
            return int((end - start).total_seconds() // 60)
        return 0

    def __str__(self):
        return f"{self.title} ({self.subject})"


def duration_minutes(self):
    if self.start_time and self.end_time:
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() // 60)
    return 0


    def __str__(self):
        return f"{self.title} ({self.date} {self.start_time})"

    class Meta:
        db_table = "class_session"
        ordering = ["-date", "-start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "date", "start_time"],
                name="unique_teacher_class_start"
            )
        ]
