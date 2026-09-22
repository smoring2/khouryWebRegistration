from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import *
from .validation import coerce_int


def _read_credentials(request):
    """Return ``(user_id, password)`` submitted on a login form.

    ``request.POST`` is read with ``.get()`` so that a missing key (or a bare
    ``GET`` on the login endpoint) cannot raise ``MultiValueDictKeyError`` and
    surface a traceback whose frame locals contain submitted credentials.
    ``user_id`` is ``None`` when it is absent or not numeric.
    """
    user_id = coerce_int(request.POST.get('username'))
    password = request.POST.get('password') or ''
    return user_id, password


def student_login_page(request):
    return render(request, 'student/student_login.html')

def student_login(request):
    if request.method != 'POST':
        return redirect('student_login_page')

    nuid, password = _read_credentials(request)
    if nuid is None or not password:
        messages.warning(request, 'Please provide a valid student ID and password.')
        return redirect('student_login_page')

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
    if request.method != 'POST':
        return redirect('advisor_login_page')

    employee_id, password = _read_credentials(request)
    if employee_id is None or not password:
        messages.warning(request, 'Please provide a valid advisor ID and password.')
        return redirect('advisor_login_page')

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
    if request.method != 'POST':
        return redirect('admin_login_page')

    employee_id, password = _read_credentials(request)
    if employee_id is None or not password:
        messages.warning(request, 'Please provide a valid admin ID and password.')
        return redirect('admin_login_page')

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
