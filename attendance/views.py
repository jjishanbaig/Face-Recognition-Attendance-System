import csv
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from .models import Employee,AttendanceRecord
from .forms import EmployeeForm
from .face_engine import save_sample,train,recognize
class AppLogin(LoginView):
    template_name="registration/login.html"
    redirect_authenticated_user=True
class AppLogout(LogoutView):
    next_page="login"
@login_required
def dashboard(request):
    today=date.today()
    return render(request,"attendance/dashboard.html",{"employee_count":Employee.objects.count(),"today_count":AttendanceRecord.objects.filter(date=today).count(),"today_records":AttendanceRecord.objects.filter(date=today).select_related("employee")[:10]})
@login_required
def employees(request):
    q=request.GET.get("q","").strip(); es=Employee.objects.all().order_by("full_name")
    if q: es=es.filter(full_name__icontains=q)|es.filter(employee_id__icontains=q)
    return render(request,"attendance/employees.html",{"employees":es.distinct(),"q":q})
@login_required
def add_employee(request):
    form=EmployeeForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        e=form.save(); messages.success(request,"Employee added. Capture face samples before training."); return redirect("employee_detail",pk=e.pk)
    return render(request,"attendance/employee_form.html",{"form":form})
@login_required
def employee_detail(request,pk):
    e=get_object_or_404(Employee,pk=pk)
    return render(request,"attendance/employee_detail.html",{"employee":e,"records":e.attendance_records.all()[:10]})
@login_required
def delete_employee(request,pk):
    e=get_object_or_404(Employee,pk=pk)
    if request.method=="POST":
        import shutil
        from django.conf import settings
        shutil.rmtree(settings.MEDIA_ROOT/"faces"/e.employee_id,ignore_errors=True); e.delete()
        messages.success(request,"Employee deleted."); return redirect("employees")
    return render(request,"attendance/delete.html",{"employee":e})
@login_required
@require_POST
def capture_api(request,pk):
    try:
        f=request.FILES.get("frame")
        if not f: return JsonResponse({"error":"No image received"},status=400)
        return JsonResponse({"ok":True,"count":save_sample(get_object_or_404(Employee,pk=pk).employee_id,f.read())})
    except Exception as ex: return JsonResponse({"error":str(ex)},status=400)
@login_required
def train_page(request):
    result=error=None
    if request.method=="POST":
        try:
            n,p=train(); result=f"Training complete: {n} samples across {p} employee(s)."
        except Exception as ex: error=str(ex)
    return render(request,"attendance/train.html",{"result":result,"error":error})
@login_required
def camera(request): return render(request,"attendance/camera.html")
@login_required
@require_POST
def recognize_api(request):
    try:
        f=request.FILES.get("frame")
        if not f: return JsonResponse({"error":"No image received"},status=400)
        return JsonResponse({"results":recognize(f.read())})
    except Exception as ex: return JsonResponse({"error":str(ex)},status=400)
@login_required
def records(request):
    rs=AttendanceRecord.objects.select_related("employee").all(); q=request.GET.get("q","").strip(); d=request.GET.get("date","").strip()
    if q: rs=rs.filter(employee__full_name__icontains=q)|rs.filter(employee__employee_id__icontains=q)
    if d: rs=rs.filter(date=d)
    return render(request,"attendance/records.html",{"records":rs.order_by("-date","-time"),"q":q,"selected_date":d})
@login_required
def export_csv(request):
    rs=AttendanceRecord.objects.select_related("employee").order_by("-date","-time"); d=request.GET.get("date","")
    if d: rs=rs.filter(date=d)
    resp=HttpResponse(content_type="text/csv"); resp["Content-Disposition"]='attachment; filename="attendance_report.csv"'
    w=csv.writer(resp); w.writerow(["Employee ID","Name","Department","Date","Time","Method"])
    for r in rs: w.writerow([r.employee.employee_id,r.employee.full_name,r.employee.department,r.date,r.time,r.method])
    return resp
