from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

from .access_control import (ROLE_ADMIN, ROLE_ADVISOR, ROLE_STUDENT,
                             end_session, start_session)
from .models import *

INVALID_CREDENTIALS_MESSAGE = 'Invalid credentials.'


def student_login_page(request):
    return render(request, 'student/student_login.html')


@require_POST
def student_login(request):
    nuid = request.POST['username']
    password = request.POST['password']
    try:
        user = Student.objects.get(nuid=nuid)
    except Student.DoesNotExist:
        # Do not disclose whether the account exists.
        messages.warning(request, INVALID_CREDENTIALS_MESSAGE)
        return redirect('student_login_page')

    if user.password == password:
        start_session(request, ROLE_STUDENT, user.nuid)
        return redirect("student_profile", user.nuid)
    else:
        messages.warning(request, INVALID_CREDENTIALS_MESSAGE)
        return redirect('student_login_page')


def advisor_login_page(request):
    return render(request, 'advisor/advisor_login.html')


@require_POST
def advisor_login(request):
    employee_id = request.POST['username']
    password = request.POST['password']
    try:
        user = Advisor.objects.get(employee_id=employee_id)
    except Advisor.DoesNotExist:
        messages.warning(request, INVALID_CREDENTIALS_MESSAGE)
        return redirect('advisor_login_page')

    if user.password == password:
        start_session(request, ROLE_ADVISOR, user.employee_id)
        return redirect("advisor_statics", user.employee_id)
    else:
        messages.warning(request, INVALID_CREDENTIALS_MESSAGE)
        return redirect('advisor_login_page')


def admin_login_page(request):
    return render(request, 'admin_template/admin_login.html')


@require_POST
def admin_login(request):
    employee_id = request.POST['username']
    password = request.POST['password']
    try:
        user = Admin.objects.get(employee_id=employee_id)
    except Admin.DoesNotExist:
        messages.warning(request, INVALID_CREDENTIALS_MESSAGE)
        return redirect('admin_login_page')

    if user.password == password:
        start_session(request, ROLE_ADMIN, user.employee_id)
        return redirect("admin_home")
    else:
        messages.warning(request, INVALID_CREDENTIALS_MESSAGE)
        return redirect('admin_login_page')


@require_POST
def logout(request):
    """Terminate the current session regardless of the principal type."""
    end_session(request)
    messages.success(request, 'You have been signed out.')
    return redirect('home_signin')
