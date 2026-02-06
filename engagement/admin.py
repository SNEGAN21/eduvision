from django.contrib import admin
from .models import EngagementReport

@admin.register(EngagementReport)
class EngagementReportAdmin(admin.ModelAdmin):
    list_display = ("session", "student", "avg_engagement", "created_at")
    list_filter = ("created_at", "session")
    search_fields = ("student__username", "session__title")
