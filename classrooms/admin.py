from django.contrib import admin
from .models import ClassSession

@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "date", "start_time", "end_time")
    list_filter = ("date", "subject")
    search_fields = ("title", "subject", "teacher__username")
