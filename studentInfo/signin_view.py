from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import *

def student_login_page(request):
    return render(request, 'student/student_login.html')

def student_login(request):
    nuid = request.POST['username']
    password = request.POST['password']
    try:
        user = Student.objects.get(nuid=nuid)
    except Student.DoesNotExist:
        # return render(request, 'student/student_login.html', {"error": "User doesn't exist."})
        messages.warning(request, 'Student with ID {} doesn"t exists!'.format(nuid))
        return redirect('student_login_page')

    if user.password == password:
        request.session['nuid'] = user.nuid
        return redirect("student_profile", user.nuid)
    else:
        messages.warning(request, 'Password is not correct')
        return redirect('student_login_page')
        # return render(request, 'student/student_login.html', {"error": "Wrong password."})

def advisor_login_page(request):
    return render(request, 'advisor/advisor_login.html')

def advisor_login(request):
    employee_id = request.POST['username']
    password = request.POST['password']
    try:
        user = Advisor.objects.get(employee_id=employee_id)
    except Advisor.DoesNotExist:
        # return render(request, 'advisor/advisor_login.html', {"error": "User doesn't exist."})
        messages.warning(request, 'Advisor with ID {} doesn"t exists!'.format(employee_id))
        return redirect('advisor_login_page')

    if user.password == password:
        request.session['employee_id'] = user.employee_id
        return redirect("advisor_statics", user.employee_id)
    else:
        # return render(request, 'advisor/advisor_login.html', {"error": "Wrong password."})
        messages.warning(request, 'Password is not correct')
        return redirect('advisor_login_page')

def admin_login_page(request):
    return render(request, 'admin_template/admin_login.html')

def admin_login(request):
    employee_id = request.POST['username']
    password = request.POST['password']
    try:
        user = Admin.objects.get(employee_id=employee_id)
    except Admin.DoesNotExist:
        # return render(request, 'admin_template/admin_login.html', {"error": "User doesn't exist."})
        messages.warning(request, 'Student with ID {} doesn"t exists!'.format(employee_id))
        return redirect('admin_login_page')

    if user.password == password:
        request.session['employee_id'] = user.employee_id
        return redirect("admin_home")
    else:
        # return render(request, 'admin_template/admin_login.html', {"error": "Wrong password."})
        messages.warning(request, 'Password is not correct')
        return redirect('admin_login_page')
