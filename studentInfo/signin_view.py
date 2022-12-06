from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from .models import *

def student_login_page(request):
    return render(request, 'student/student_login.html')

def student_login(request):
    nuid = request.POST['username']
    password = request.POST['password']
    try:
        user = Student.objects.get(nuid=nuid)
    except Student.DoesNotExist:
        return render(request, 'student/student_login.html', {"error": "User doesn't exist."})

    if user.password == password:
        request.session['nuid'] = user.nuid
        return redirect("student_profile", user.nuid)
    else:
        return render(request, 'student/student_login.html', {"error": "Wrong password."})

def advisor_login_page(request):
    return render(request, 'advisor/advisor_login.html')

def advisor_login(request):
    employee_id = request.POST['username']
    password = request.POST['password']
    try:
        user = Advisor.objects.get(employee_id=employee_id)
    except Advisor.DoesNotExist:
        return render(request, 'advisor/advisor_login.html', {"error": "User doesn't exist."})

    if user.password == password:
        request.session['employee_id'] = user.employee_id
        return redirect("advisor_profile", user.employee_id)
    else:
        return render(request, 'advisor/advisor_login.html', {"error": "Wrong password."})

def admin_login_page(request):
    return render(request, 'admin_template/admin_login.html')

def admin_login(request):
    employee_id = request.POST['username']
    password = request.POST['password']
    try:
        user = Admin.objects.get(nuemployee_id=employee_id)
    except Admin.DoesNotExist:
        return render(request, 'admin_template/admin_login.html', {"error": "User doesn't exist."})

    if user.password == password:
        request.session['employee_id'] = user.employee_id
        return redirect("admin_home")
    else:
        return render(request, 'admin_template/admin_login.html', {"error": "Wrong password."})
