from django.urls import path
from . import views
urlpatterns=[
 path("",views.dashboard,name="dashboard"),path("login/",views.AppLogin.as_view(),name="login"),path("logout/",views.AppLogout.as_view(),name="logout"),
 path("employees/",views.employees,name="employees"),path("employees/add/",views.add_employee,name="add_employee"),
 path("employees/<int:pk>/",views.employee_detail,name="employee_detail"),path("employees/<int:pk>/delete/",views.delete_employee,name="delete_employee"),
 path("api/employees/<int:pk>/capture/",views.capture_api,name="capture_api"),path("train/",views.train_page,name="train"),
 path("camera/",views.camera,name="camera"),path("api/recognize/",views.recognize_api,name="recognize_api"),
 path("attendance/",views.records,name="records"),path("attendance/export.csv",views.export_csv,name="export_csv")]
