from django.shortcuts import render
from .models import Student, Registration
from django.views.generic import ListView, DetailView
from django.db import connection
from django.http import HttpResponse


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
    if len(res['pending_list']) == 0:
        res['pending_list'] = ['No courses']

    context = {
        "data": res
    }

    return render(request, 'student/student_notification.html', context)


def dropCourse(request, student_id):
    cursor = connection.cursor()
    course_currently_taking = getCourseCurrentlyTakingOrPending(student_id)
    if request.method == 'POST':
        nuid = student_id
        course_id = int(request.POST['course_number'])
        advisor_id = getAdvisorByStudentId(student_id)

        cursor.execute('''SELECT * from registration''')
        all_registration_info = cursor.fetchall()

        if course_id not in course_currently_taking:
            return HttpResponse('You cannot drop this course')
        elif nuid != student_id:
            return HttpResponse('Please correct your niud.')
        else:

            cursor.execute('''DELETE FROM registration WHERE nuid = %(nuid)s AND course_id = %(course_id)s ''',
                           {'nuid': nuid, 'course_id': course_id})
            return HttpResponse('deleted')

    res = {
        'student_id': int(student_id),
        'course_taking': [],
    }

    for course in range(len(course_currently_taking)):
        res['course_taking'].append(str(course_currently_taking[course]) + ':     ' +
                                    getNameByCourseNum(course_currently_taking[course]))

    context = {
        "data": res
    }

    cursor.close()
    return render(request, 'student/drop_course.html', context)


def getDegreeAudit(request, student_id):
    cursor = connection.cursor()
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
                str_builder = "Course: " + str(comp[1]) + "     " + grade_map[sh]
                res['completed_list'].append(str_builder)


    res['cumulative'].append("Cumulative: " + str(cum_sh) + "      " + str(cum_gpa))
    if cum_sh == 0:
        res['overall_gpa'].append("Overall GPA: " + str(0))
    else:
        res['overall_gpa'].append("Overall GPA: " + str(calculateStudentGpa(student_id)))
        updateStudentGpa(student_id)

    context = {
        "data": res
    }

    cursor.close()
    return render(request, 'student/degree_audit.html', context)


def getRegistrationInfo(request, student_id):
    cursor = connection.cursor()
    # Submit course registration form.
    if request.method == 'POST':
        nuid = student_id
        course_id = int(request.POST['course_number'])
        advisor_id = getAdvisorByStudentId(student_id)

        cursor.execute('''SELECT * from registration''')
        all_registration_info = cursor.fetchall()
        cursor.execute('''SELECT employee_id from advisor''')
        advisor_list = cursor.fetchall()

        # Invalid case 1: Student has submitted course registration form or has taken previously.
        for i in range(len(all_registration_info)):
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
            string_builder = "Course Number: " + str(course_id[0]) + "   " + course_id[1] + \
            "   Meeting time: " + str(course_id[2]) + "   Capacity: " + str(course_id[4]) + \
                "   Registered: " + str(course_id[6])
            res['course_list'].append(string_builder)

    res['complete_courses'] = getCompleteCoursesByNuid(nuid)

    context = {
        "data": res
    }

    cursor.close()
    return render(request, 'student/course_registration.html', context)


# This method takes two variable, arr stands for a fetched two dimensional array,
# check if the emplpoyee_id is a valid or not.
def isValidAdvisorId(arr, employee_id):
    for i in range(len(arr)):
        if employee_id == arr[i][0]:
            return True

    return False


def getNameByCourseNum(course_id):
    cursor = connection.cursor()
    course_id = {'course_id': course_id}
    cursor.execute('''SELECT course_name FROM course WHERE course_id = %(course_id)s''', course_id)
    cursor.close()

    return cursor.fetchall()[0][0]


# Retrieve all information from the course list.
def getCourseList():
    cursor = connection.cursor()
    res = []
    cursor.execute('''SELECT * FROM course''')
    course_list = cursor.fetchall()
    if course_list:
        for course_id in course_list:
            res.append(course_id)

    cursor.close()
    return res


# Input takes student NUID, query the registration table, retrieve all courses id that the student has completed.
def getCompleteCoursesByNuid(student_id):
    cursor = connection.cursor()
    res = []
    student_id = {'student_id': student_id}
    cursor.execute('''SELECT course_id FROM registration WHERE nuid = %(student_id)s AND status = 'completed' ''',
                   student_id)
    results = cursor.fetchall()

    if results:
        for r in results:
            res.append(r[0])
    cursor.close()

    return res


# Input takes a student NUID, get all course numbers that the student submitted registration form and still pending
# for advisor approval.
def getPendingApprovals(student_id):
    cursor = connection.cursor()
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

    cursor.close()
    return res


def getAdvisorByStudentId(student_id):
    cursor = connection.cursor()
    student_id = {'student_id': student_id}
    cursor.execute('''SELECT advisor FROM student WHERE nuid = %(student_id)s''', student_id)
    cursor.close()
    return cursor.fetchall()[0][0]


def isCourseFull(course_id):
    cursor = connection.cursor()
    course_id = {'course_id': course_id}
    cursor.execute('''SELECT max_num_of_students FROM course WHERE course_id = %(course_id)s''', course_id)
    cap = cursor.fetchall()[0][0]
    cursor.execute('''SELECT registered_num_of_stud FROM course WHERE course_id = %(course_id)s''', course_id)
    cur_num = cursor.fetchall()[0][0]
    cursor.close()
    return cur_num >= cap


def getCourseInProgress(student_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT course_id FROM registration WHERE nuid = %(student_id)s AND status = 'approved'
    ''', {'student_id': student_id})
    res = cursor.fetchall()
    cursor.close()

    if res:
        return res[0]

    return []

def getCourseCurrentlyTakingOrPending(student_id):
    cursor = connection.cursor()
    res = []
    cursor.execute('''SELECT course_id FROM registration where nuid = %(student_id)s AND status != 'completed'
    ''', {'student_id': student_id})
    for c in cursor.fetchall():
        res.append(c[0])
    cursor.close()
    return res


# Given a student nuid, check if this nuid in student list.
def isValidNuid(student_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT nuid FROM student''')
    cursor.close()

    return student_id in cursor[0]

# Given student id, calculate the cumulative GPA that student have so far.
def calculateStudentGpa(student_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM registration WHERE status = 'completed' ''')
    comp_list = cursor.fetchall()

    cum_sh = 0
    cum_gpa = 0.0

    if comp_list:
        for comp in comp_list:
            if comp[0] == int(student_id):

                cursor.execute('''SELECT semester_hrs FROM course WHERE course_id = %(course_id)s''',
                               {'course_id': comp[1]})
                # Semester hours.
                sh = cursor.fetchall()[0][0]
                cum_sh += sh
                cum_gpa += sh * min(4.0, comp[3])

    if cum_sh == 0:
        return 0
    cursor.close()
    return round(cum_gpa / cum_sh, 2)


def updateStudentGpa(student_id):
    cursor = connection.cursor()
    gpa = calculateStudentGpa(student_id)
    cursor.execute('''UPDATE student SET grade = %(gpa)s WHERE nuid = %(student_id)s ''',
                   {'gpa' : gpa, 'student_id' : student_id})
    cursor.close()
