from django.shortcuts import render
from .models import Student, Registration
from django.views.generic import ListView, DetailView
from django.db import connection
from django.http import HttpResponse
cursor= connection.cursor()

def testmysql(request):
    myStudent = Student.objects.all()
    context = {
        'student_name': myStudent[0].name,
    }
    return render(request, 'studentInfo.html', context)

# StudentList class should be deleted later on.
class StudentList(ListView):
    template_name= 'student/student_list.html'
    model = Student

# Student home page.
class StudentHome(DetailView):
    template_name = 'student/student_home.html'
    model = Student
# Student main page after logging in.
class StudentDetails(DetailView):
    template_name = 'student/student_profile.html'
    model = Student

class StudentRegistration(DetailView):
    template_name = 'student/course_registration.html'
    model = Student

def dropCourse(request, student_id):
    if request.method == 'POST':
        nuid = int(request.POST['s_nuid'])
        course_id = int(request.POST['course_number'])
        advisor_id = int(request.POST['advisor_id'])

        cursor.execute('''SELECT * from registration''')
        all_registration_info = cursor.fetchall()
        cursor.execute('''SELECT employee_id from advisor''')
        advisor_list = cursor.fetchall()

        if nuid in all_registration_info[0] and course_id in all_registration_info[1] and advisor_id in all_registration_info[2]:
            return HttpResponse('Error, you cannot submit the same form.')
        elif nuid != student_id:
            return HttpResponse('Please correct your niud.')
        elif nuid in all_registration_info[0] and course_id not in all_registration_info[1]:
            return HttpResponse('You cannot drop this course')
        else:
            Registration.objects.create(nuid = nuid, course_id = course_id, advisor_id = advisor_id, status = 'drop')

    res = {
        'student_id': int(student_id),
    }

    context = {
        "data": res
    }

    return render(request, 'student/drop_course.html', context)

def getDegreeAudit(request, student_id):
    res = {
        'student_id': int(student_id),
        'completed_list': [],
    }

    cursor.execute('''SELECT * FROM registration WHERE status = 'completed' ''')
    comp_list = cursor.fetchall()

    grade_map = {4.00 : 'A', 3.66 : 'A-', 3.33: 'B+', 3: 'B', 2.66: 'B-', 2.33: 'C+', 2.00: 'C', 1.66: 'C-',
                 1.33: 'D+', 1.00: 'D', 0: 'F'}

    cum_sh = 0
    cum_gpa = 0.0

    if comp_list:
        for comp in comp_list:
            if comp[0] == int(student_id):
                course_id = comp[1]
                course_id = {'course_id': int(course_id)}
                cursor.execute('''SELECT semester_hrs FROM course WHERE course_id = %(course_id)s''', course_id)
                # Semester hours.
                sh = cursor.fetchall()[0][0]
                cum_sh += sh
                cum_gpa += sh * comp[3]
                str_builder = "Course: " + str(comp[1]) + "                                       " + grade_map[sh]
                res['completed_list'].append(str_builder)


    res['completed_list'].append("Cumulative: " + str(cum_sh) + "           " + str(cum_gpa))
    res['completed_list'].append("Overall GPA: " + str(cum_gpa / cum_sh))

    context = {
        "data": res
    }

    return render(request, 'student/degree_audit.html', context)

def getRegistrationInfo(request, student_id):
    # Submit course registration form.
    if request.method == 'POST':
        nuid = int(request.POST['s_nuid'])
        course_id = int(request.POST['course_number'])
        advisor_id = int(request.POST['advisor_id'])

        cursor.execute('''SELECT * from registration''')
        all_registration_info = cursor.fetchall()
        cursor.execute('''SELECT employee_id from advisor''')
        advisor_list = cursor.fetchall()
        # num_regis = {'course_num': course_id}
        # cursor.execute('''SELECT registered_num_of_stud FROM course WHERE course_id = %(course_num)s''', num_regis)
        # num_regis = 10
        # Invalid cases:
        if nuid in all_registration_info[0] and course_id in all_registration_info[1] and advisor_id in all_registration_info[2]:
            return HttpResponse('Error, you cannot submit the same form.')
        elif nuid != student_id:
            return HttpResponse('You cannot help others to register courses.')
        # elif advisor_id not in advisor_list:
        #    return HttpResponse('Please re-enter your advisor id.')
        else:
            Registration.objects.create(nuid = nuid, course_id = course_id, advisor_id = advisor_id, status = 'pending')

    nuid = int(student_id)
    res = {
        'student_id': int(nuid),
        'course_list': [],
        'complete_courses': [],
        'pending_list': [],
    }

    cursor.execute('''SELECT * FROM course''')
    course_list = cursor.fetchall()
    if course_list:
        for course_id in course_list:
            employee_id = {'employee_id': course_id[1]}
            cursor.execute('''SELECT name FROM instructor WHERE employee_id = %(employee_id)s''', employee_id)

            string_builder = "Course Number: " + str(course_id[0]) + "   " + course_id[1] + \
            "   Meeting time: " + str(course_id[2]) + "   Capacity: " + str(course_id[3]) + \
                "   Registered: " + str(course_id[6])
            res['course_list'].append(string_builder)

    student_id = {'student_id': int(student_id)}
    cursor.execute('''SELECT course_id FROM registration WHERE nuid = %(student_id)s AND grade >= 1.0''',
                   student_id)
    results = cursor.fetchall()
    if results:
        for r in results:
            res['complete_courses'].append(r[0])


    cursor.execute('''SELECT course_id FROM registration WHERE status = 'pending' AND nuid = %(student_id)s''', student_id)
    pending_list = cursor.fetchall()
    if pending_list:
        for r in pending_list:
            if r[0] in res['pending_list']:
                continue
            res['pending_list'].append(r[0])

    context = {
        "data": res
    }

    return render(request, 'student/course_registration.html', context)
