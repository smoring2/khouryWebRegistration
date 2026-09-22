from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .access_control import login_advisor, login_admin, login_student, logout
from .models import *

# Shown to the user for both "unknown account" and "wrong password" so the login
# form does not disclose which identifiers exist.
INVALID_CREDENTIALS = 'Invalid credentials.'

def student_login_page(request):
    return render(request, 'student/student_login.html')

def student_login(request):
    nuid = request.POST['username']
    password = request.POST['password']
    try:
        user = Student.objects.get(nuid=nuid)
    except Student.DoesNotExist:
        messages.warning(request, INVALID_CREDENTIALS)
        return redirect('student_login_page')

    if user.password == password:
        login_student(request, user)
        return redirect("student_profile", user.nuid)
    else:
        messages.warning(request, INVALID_CREDENTIALS)
        return redirect('student_login_page')

def advisor_login_page(request):
    return render(request, 'advisor/advisor_login.html')

def advisor_login(request):
    employee_id = request.POST['username']
    password = request.POST['password']
    try:
        user = Advisor.objects.get(employee_id=employee_id)
    except Advisor.DoesNotExist:
        messages.warning(request, INVALID_CREDENTIALS)
        return redirect('advisor_login_page')

    if user.password == password:
        login_advisor(request, user)
        return redirect("advisor_statics", user.employee_id)
    else:
        messages.warning(request, INVALID_CREDENTIALS)
        return redirect('advisor_login_page')

def admin_login_page(request):
    return render(request, 'admin_template/admin_login.html')

def admin_login(request):
    employee_id = request.POST['username']
    password = request.POST['password']
    try:
        user = Admin.objects.get(employee_id=employee_id)
    except Admin.DoesNotExist:
        messages.warning(request, INVALID_CREDENTIALS)
        return redirect('admin_login_page')

    if user.password == password:
        login_admin(request, user)
        return redirect("admin_home")
    else:
        messages.warning(request, INVALID_CREDENTIALS)
        return redirect('admin_login_page')

def sign_out(request):
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('home_signin')
