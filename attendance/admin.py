from django.contrib import admin
from .models import Employee, AttendanceRecord
admin.site.register(Employee)
@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display=("employee","date","time","method")
    list_filter=("date","method")
    search_fields=("employee__full_name","employee__employee_id")
