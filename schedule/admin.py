from django.contrib import admin
from .models import Course, Schedule, Selection


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'kind', 'err_count', 'table_view')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'course_name', 'professor', 'start_time', 'end_time', 'location')


@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    pass
