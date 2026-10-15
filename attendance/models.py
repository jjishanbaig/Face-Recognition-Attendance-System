from django.db import models
from django.utils import timezone
from pathlib import Path
class Employee(models.Model):
    employee_id=models.CharField(max_length=40,unique=True)
    full_name=models.CharField(max_length=120)
    department=models.CharField(max_length=100,blank=True)
    email=models.EmailField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.employee_id} - {self.full_name}"
    @property
    def sample_count(self):
        from django.conf import settings
        p=settings.MEDIA_ROOT/"faces"/self.employee_id
        return len(list(p.glob("*.jpg"))) if p.exists() else 0
class AttendanceRecord(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="attendance_records")
    date=models.DateField(default=timezone.localdate)
    time=models.TimeField(default=timezone.localtime)
    method=models.CharField(max_length=30,default="Face Recognition")
    class Meta:
        constraints=[models.UniqueConstraint(fields=["employee","date"],name="one_attendance_per_employee_per_day")]
        ordering=["-date","-time"]
