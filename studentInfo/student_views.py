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


def getStudentNotification(request, student_id):
    res = {
        'student_id': int(student_id),
        'pending_list': [],
    }

    for r in getPendingApprovals(student_id):
        res['pending_list'].append(str(r) + "            " + getNameByCourseNum(r))

    context = {
        "data": res
    }

    return render(request, 'student/student_notification.html', context)


def dropCourse(request, student_id):
    if request.method == 'POST':
        nuid = int(request.POST['s_nuid'])
        course_id = int(request.POST['course_number'])
        advisor_id = getAdvisorByStudentId(student_id)

        cursor.execute('''SELECT * from registration''')
        all_registration_info = cursor.fetchall()

        if nuid in all_registration_info[0] and course_id in all_registration_info[1] and advisor_id in all_registration_info[2]:
            return HttpResponse('Error, you cannot submit the same form.')
        elif nuid != student_id:
            return HttpResponse('Please correct your niud.')
        else:
            drop_course = Registration.objects.get(course=course_id, nuid=nuid)
            drop_course.delete()
            return HttpResponse('deleted')

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
        'overall_gpa': [],
        'cumulative': [],
        'in_progress': getCourseInProgress(student_id),
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
                cum_gpa += sh * min(4.0, comp[3])
                str_builder = "Course: " + str(comp[1]) + "                                       " + grade_map[sh]
                res['completed_list'].append(str_builder)


    res['cumulative'].append("Cumulative: " + str(cum_sh) + "           " + str(cum_gpa))
    if cum_sh == 0:
        res['overall_gpa'].append("Overall GPA: " + str(0))
    else:
        res['overall_gpa'].append("Overall GPA: " + str(cum_gpa / cum_sh))

    context = {
        "data": res
    }

    return render(request, 'student/degree_audit.html', context)


def getRegistrationInfo(request, student_id):
    # Submit course registration form.
    if request.method == 'POST':
        nuid = int(request.POST['s_nuid'])
        course_id = int(request.POST['course_number'])
        advisor_id = getAdvisorByStudentId(student_id)

        cursor.execute('''SELECT * from registration''')
        all_registration_info = cursor.fetchall()
        cursor.execute('''SELECT employee_id from advisor''')
        advisor_list = cursor.fetchall()

        # Invalid case 1: Student has submitted course registration form or has taken previously.
        for i in range(len(all_registration_info[0])):
            if nuid == all_registration_info[i][0] and course_id == all_registration_info[i][1]:
                return HttpResponse('Error, you cannot submit the same form.')
        # Invalid case 2: The nuid student input is not his/ her own.
        if nuid != student_id:
            return HttpResponse('You cannot help others to register courses.')
        elif not isValidAdvisorId(advisor_list, advisor_id):
            return HttpResponse('Please re-enter your advisor id.')
        elif isCourseFull(course_id):
            return HttpResponse('The course you registered for has reached the capacity')
        else:
            Registration.objects.create(nuid = nuid, course_id = course_id, advisor_id = advisor_id, grade = None,
                                        status = 'pending')
            return HttpResponse("Registration succeed, please waiting the advisor for approval")

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
            "   Meeting time: " + str(course_id[2]) + "   Capacity: " + str(course_id[4]) + \
                "   Registered: " + str(course_id[6])
            res['course_list'].append(string_builder)

    res['complete_courses'] = getCompleteCoursesByNuid(nuid)

    context = {
        "data": res
    }

    return render(request, 'student/course_registration.html', context)


# This method takes two variable, arr stands for a fetched two dimensional array,
# check if the emplpoyee_id is a valid or not.
def isValidAdvisorId(arr, employee_id):
    for i in range(len(arr)):
        if employee_id == arr[i][0]:
            return True

    return False


def getNameByCourseNum(course_id):
    course_id = {'course_id': course_id}
    cursor.execute('''SELECT course_name FROM course WHERE course_id = %(course_id)s''', course_id)
    return cursor.fetchall()[0][0]


# Retrieve all information from the course list.
def getCourseList():
    res = []
    cursor.execute('''SELECT * FROM course''')
    course_list = cursor.fetchall()
    if course_list:
        for course_id in course_list:
            res.append(course_id)

    return res


# Input takes student NUID, query the registration table, retrieve all courses id that the student has completed.
def getCompleteCoursesByNuid(student_id):
    res = []
    student_id = {'student_id': student_id}
    cursor.execute('''SELECT course_id FROM registration WHERE nuid = %(student_id)s AND status = 'completed' ''',
                   student_id)
    results = cursor.fetchall()

    if results:
        for r in results:
            res.append(r[0])

    return res


# Input takes a student NUID, get all course numbers that the student submitted registration form and still pending
# for advisor approval.
def getPendingApprovals(student_id):
    res = []
    student_id = {'student_id': int(student_id)}
    cursor.execute('''SELECT course_id FROM registration WHERE status = 'pending' AND nuid = %(student_id)s''',
                   student_id)
    pending_list = cursor.fetchall()
    if pending_list:
        for r in pending_list:
            if r[0] in res:
                continue
            res.append(r[0])

    return res


def getAdvisorByStudentId(student_id):
    student_id = {'student_id': student_id}
    cursor.execute('''SELECT advisor FROM student WHERE nuid = %(student_id)s''', student_id)
    return cursor.fetchall()[0][0]


def isCourseFull(course_id):
    course_id = {'course_id': course_id}
    cursor.execute('''SELECT max_num_of_students FROM course WHERE course_id = %(course_id)s''', course_id)
    cap = cursor.fetchall()[0][0]
    cursor.execute('''SELECT registered_num_of_stud FROM course WHERE course_id = %(course_id)s''', course_id)
    cur_num = cursor.fetchall()[0][0]
    return cur_num >= cap


def getCourseInProgress(student_id):
    res = []
    student_id = {'student_id': student_id}
    cursor.execute('''SELECT course_id FROM registration WHERE nuid = %(student_id)s AND status = 'approved'
    ''', student_id)
    l = cursor.fetchall()
    for course in l:
        res.append(course)
    if len(l) == 0:
        return []
    return l[0]
