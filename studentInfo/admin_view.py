from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .admin_form import *
from .models import *


def admin_home(request):
    total_students = Student.objects.all().count()
    total_course = Course.objects.all().count()
    total_advisor = Advisor.objects.all().count()
    total_instructor = Instructor.objects.all().count()
    total_department = Department.objects.all().count()
    context = {
        'page_title': "Admin",
        'total_students': total_students,
        'total_course': total_course,
        'total_advisor': total_advisor,
        'total_department': total_department,
        'total_instructor': total_instructor
    }
    return render(request, 'admin_template/home.html', context)


def add_advisor(request):
    form = AdvisorForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Advisor'}
    if request.method == 'POST':
        if form.is_valid():
            employee_id = form.cleaned_data.get('employee_id')
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            department = form.cleaned_data.get('department')
            password = form.cleaned_data.get('password')
            try:
                user = Advisor.objects.create(employee_id=employee_id, name=name, email=email, phone=phone, department=department, password=password)
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_advisor'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'admin_template/add_advisor_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            nuid = student_form.cleaned_data.get('nuid')
            name = student_form.cleaned_data.get('name')
            email = student_form.cleaned_data.get('email')
            bdate = student_form.cleaned_data.get('bdate')
            campusid = student_form.cleaned_data.get('campusid')
            collegeid = student_form.cleaned_data.get('collegeid')
            department = student_form.cleaned_data.get('department')
            phone = student_form.cleaned_data.get('phone')
            advisor = student_form.cleaned_data.get('advisor')
            grade = student_form.cleaned_data.get('grade')
            semesterhour = student_form.cleaned_data.get('semesterhour')
            password = student_form.cleaned_data.get('password')
            try:
                user = Student.objects.create(nuid=nuid, name=name, 
                    email=email, bdate=bdate, campusid=campusid, collegeid=collegeid, department=department, phone=phone, advisor=advisor, grade=grade, semesterhour=semesterhour, password=password)
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'admin_template/add_student_template.html', context)


def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            course_id = form.cleaned_data.get('course_id')
            course_name = form.cleaned_data.get('course_name')
            instructor = form.cleaned_data.get('instructor')
            meeting_time = form.cleaned_data.get('meeting_time')
            max_num_of_students = form.cleaned_data.get('max_num_of_students')
            semester = form.cleaned_data.get('semester')
            semester_hrs = form.cleaned_data.get('semester_hrs')
            registered_num_of_stud = form.cleaned_data.get('registered_num_of_stud')
            department = form.cleaned_data.get('department')
            campusid = form.cleaned_data.get('campusid')
            building = form.cleaned_data.get('building')
            room = form.cleaned_data.get('room')
            date = form.cleaned_data.get('date')
            try:
                course = Course()
                course.course_id = course_id
                course.course_name = course_name
                course.instructor = instructor
                course.meeting_time = meeting_time
                course.max_num_of_students = max_num_of_students
                course.semester = semester
                course.semester_hrs = semester_hrs
                course.registered_num_of_stud = registered_num_of_stud
                course.department = department
                course.campusid = campusid
                course.building = building
                course.room = room
                course.date = date
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add course")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'admin_template/add_course_template.html', context)


def manage_advisor(request):
    advisors = Advisor.objects.all()
    context = {
        'advisors': advisors,
        'page_title': 'Manage Advisor'
    }
    return render(request, "admin_template/manage_advisor_template.html", context)


def manage_student(request):
    students = Student.objects.all()
    context = {
        'students': students,
        'page_title': 'Manage Students'
    }
    return render(request, "admin_template/manage_student_template.html", context)


def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "admin_template/manage_course_template.html", context)


def edit_advisor(request, employee_id):
    advisor = get_object_or_404(Advisor, employee_id=employee_id)
    form = AdvisorForm(request.POST or None, instance=advisor)
    context = {
        'form': form,
        'employee_id': employee_id,
        'page_title': 'Edit Advisor'
    }
    if request.method == 'POST':
        if form.is_valid():
            employee_id = form.cleaned_data.get('employee_id')
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            department = form.cleaned_data.get('department')
            password = form.cleaned_data.get('password') or None
            try:
                user = Advisor.objects.get(employee_id=advisor.employee_id)
                user.employee_id = employee_id
                user.name = name
                user.email = email
                user.phone = phone
                user.department = department
                if password != None:
                    user.set_password(password)
                user.save()
                advisor.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_advisor', args=[employee_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fill form properly")
    else:
        return render(request, "admin_template/edit_advisor_template.html", context)


def edit_student(request, nuid):
    student = get_object_or_404(Student, nuid=nuid)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'nuid': nuid,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            nuid = form.cleaned_data.get('nuid')
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            bdate = form.cleaned_data.get('bdate')
            campusid = form.cleaned_data.get('campusid')
            collegeid = form.cleaned_data.get('collegeid')
            department = form.cleaned_data.get('department')
            phone = form.cleaned_data.get('phone')
            advisor = form.cleaned_data.get('advisor')
            grade = form.cleaned_data.get('grade')
            semesterhour = form.cleaned_data.get('semesterhour')
            password = form.cleaned_data.get('password')
            try:
                user = Student.objects.get(nuid=student.nuid)
                user.nuid = nuid
                user.name = name
                user.email = email
                user.bdate = bdate
                user.campusid = campusid
                user.collegeid = collegeid
                user.department = department
                user.phone = phone
                user.advisor = advisor
                user.grade = grade
                user.semesterhour = semesterhour
                if password != None:
                    user.set_password(password)
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[nuid]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "admin_template/edit_student_template.html", context)


def edit_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    form = CourseForm(request.POST or None, instance=course)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            course_id = form.cleaned_data.get('course_id')
            course_name = form.cleaned_data.get('course_name')
            instructor = form.cleaned_data.get('instructor')
            meeting_time = form.cleaned_data.get('meeting_time')
            max_num_of_students = form.cleaned_data.get('max_num_of_students')
            semester = form.cleaned_data.get('semester')
            semester_hrs = form.cleaned_data.get('semester_hrs')
            registered_num_of_stud = form.cleaned_data.get('registered_num_of_stud')
            department = form.cleaned_data.get('department')
            campusid = form.cleaned_data.get('campusid')
            building = form.cleaned_data.get('building')
            room = form.cleaned_data.get('room')
            date = form.cleaned_data.get('date')
            try:
                course = Course.objects.get(course_id=course_id)
                course.course_id = course_id
                course.course_name = course_name
                course.instructor = instructor
                course.meeting_time = meeting_time
                course.max_num_of_students = max_num_of_students
                course.semester = semester
                course.semester_hrs = semester_hrs
                course.registered_num_of_stud = registered_num_of_stud
                course.department = department
                course.campusid = campusid
                course.building = building
                course.room = room
                course.date = date
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'admin_template/edit_course_template.html', context)


def delete_advisor(request, employee_id):
    advisor = get_object_or_404(Advisor, employee_id=employee_id)
    advisor.delete()
    messages.success(request, "Advisor deleted successfully!")
    return redirect(reverse('manage_advisor'))


def delete_student(request, nuid):
    student = get_object_or_404(Student, nuid=nuid)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    course.delete()
    messages.success(request, "Course deleted successfully!")
    return redirect(reverse('manage_course'))