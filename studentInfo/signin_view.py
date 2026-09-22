from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import *

CREDENTIALS_REQUIRED = 'Please provide both an ID and a password.'
INVALID_ID = 'The ID must be numeric.'


def _get_credentials(request):
    """Read the submitted credentials without letting a missing key raise.

    ``request.POST['username']`` raises ``MultiValueDictKeyError`` when the key
    is absent, and the resulting technical 500 page would expose the submitted
    password in the traceback frame locals.
    """
    user_id = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    return user_id, password


def student_login_page(request):
    return render(request, 'student/student_login.html')


@require_POST
def student_login(request):
    nuid, password = _get_credentials(request)
    if not nuid or not password:
        messages.warning(request, CREDENTIALS_REQUIRED)
        return redirect('student_login_page')
    if not nuid.isdigit():
        messages.warning(request, INVALID_ID)
        return redirect('student_login_page')

    try:
        user = Student.objects.get(nuid=int(nuid))
    except (Student.DoesNotExist, ValueError):
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


@require_POST
def advisor_login(request):
    employee_id, password = _get_credentials(request)
    if not employee_id or not password:
        messages.warning(request, CREDENTIALS_REQUIRED)
        return redirect('advisor_login_page')
    if not employee_id.isdigit():
        messages.warning(request, INVALID_ID)
        return redirect('advisor_login_page')

    try:
        user = Advisor.objects.get(employee_id=int(employee_id))
    except (Advisor.DoesNotExist, ValueError):
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


@require_POST
def admin_login(request):
    employee_id, password = _get_credentials(request)
    if not employee_id or not password:
        messages.warning(request, CREDENTIALS_REQUIRED)
        return redirect('admin_login_page')
    if not employee_id.isdigit():
        messages.warning(request, INVALID_ID)
        return redirect('admin_login_page')

    try:
        user = Admin.objects.get(employee_id=int(employee_id))
    except (Admin.DoesNotExist, ValueError):
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
