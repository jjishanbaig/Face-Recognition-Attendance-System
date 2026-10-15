# Generated initial schema for the local attendance project.
import django.db.models.deletion
from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employee_id", models.CharField(max_length=40, unique=True)),
                ("full_name", models.CharField(max_length=120)),
                ("department", models.CharField(blank=True, max_length=100)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="AttendanceRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=django.utils.timezone.localdate)),
                ("time", models.TimeField(default=django.utils.timezone.localtime)),
                ("method", models.CharField(default="Face Recognition", max_length=30)),
                ("employee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to="attendance.employee")),
            ],
            options={"ordering": ["-date", "-time"]},
        ),
        migrations.AddConstraint(
            model_name="attendancerecord",
            constraint=models.UniqueConstraint(fields=("employee", "date"), name="one_attendance_per_employee_per_day"),
        ),
    ]
