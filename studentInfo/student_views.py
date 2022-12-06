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
    template_name = 'student/student_list.html'
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
        res['pending_list'].append({'course_num': r, 'course_name': getNameByCourseNum(r),
                                    'status': 'Pending for approval'})

    context = {
        "data": res
    }

    return render(request, 'student/student_notification.html', context)


def dropCourse(request, student_id):
    removeRejFromRegistration()
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
            return HttpResponse('Drop succeed')

    res = {
        'student_id': int(student_id),
        'course_taking': [],
    }

    for course in range(len(course_currently_taking)):
        res['course_taking'].append({'course_num': str(course_currently_taking[course]), 'course_name':
                                    getNameByCourseNum(course_currently_taking[course]),
                                    'status': getStudentCourseStatus(student_id, course_currently_taking[course])})

    context = {
        "data": res
    }

    cursor.close()
    return render(request, 'student/drop_course.html', context)


def getDegreeAudit(request, student_id):
    cursor = connection.cursor()
    res = {
        'student_id': int(student_id),
        'overall_gpa': [],
        'in_progress': [],
        'complete_list': [],
        'grade': [],
        'cumulative_pts': [],
        'cumulative_sh': [],
    }

    # Build in progress print list.
    for ea in getCourseInProgress(student_id):
        res['in_progress'].append({'course_id': str(ea), 'course_name': getNameByCourseNum(ea), 'grade': 'IP'})

    # Get course list that the student have completed.
    cursor.execute('''SELECT * FROM registration WHERE (status = 'failed' OR status = 'completed') ''')
    comp_list = cursor.fetchall()

    # grade_map = {4.00: 'A', 3.66: 'A-', 3.33: 'B+', 3: 'B', 2.66: 'B-', 2.33: 'C+', 2.00: 'C', 1.66: 'C-',
    #             1.33: 'D+', 1.00: 'D', 0: 'F'}

    cum_sh = 0
    cum_gpa = 0.0

    for comp in comp_list:
        if comp[0] == int(student_id):
            course_id = comp[1]
            course_id = {'course_id': int(course_id)}
            cursor.execute('''SELECT semester_hrs FROM course WHERE course_id = %(course_id)s''', course_id)
            # Semester hours.
            sh = cursor.fetchall()[0][0]
            cum_sh += sh
            cum_gpa += sh * min(4.0, comp[3])
            res['complete_list'].append({'course_id': comp[1], 'grade': getGrade(comp[3]),
                                        'course_name': getCourseNameByCourseNum(comp[1]),
                                        'points_earned': sh * min(4.0, comp[3])})

    res['cumulative_sh'].append("Cumulative Semester Hours: " + str(cum_sh))
    res['cumulative_pts'].append("Cumulative Points: " + str(round(cum_gpa, 2)))
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
        if course_id not in getCourseNumList():
            return HttpResponse(str(getCourseNumList()) + 'Course number you put is not in the course list, please'
                                                          'input a correct course num.')
        # Invalid case 2: The nuid student input is not his/ her own.
        elif nuid != student_id:
            return HttpResponse('You cannot help others to register courses.')
        elif isCourseFull(course_id):
            return HttpResponse('The course you registered for has reached the capacity')
        elif isConflict(student_id, course_id):
            return HttpResponse('There is a time conflict on your schedule, you cannot register this course')
        else:
            Registration.objects.create(nuid=nuid, course_id=course_id, advisor_id=advisor_id, grade=None,
                                        status='pending')
            return HttpResponse("Registration succeed, please waiting the advisor for approval")

    nuid = int(student_id)
    res = {
        'student_id': int(nuid),
        'course_list': [],
        'complete_courses': [],
        'pending_list': [],
    }

    for course in getAllCourseInfo():
        res['course_list'].append({'course_num': course[0], 'course_name': course[1],
                                   'instructor': getInstructorNameById(course[2]), 'meeting_time': str(course[3]),
                                   'date': course[12],
                                   'capacity': course[4], 'semester': course[5],
                                   'semester_hrs': course[6],
                                   'cur_registered': course[7]})

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


# Student Table
# Get student id list.
def getStudentIdList():
    cursor = connection.cursor()
    cursor.execute('''SELECT nuid FROM student''')
    res = cursor.fetchall()
    cursor.close()

    return res[0]


# Given a student nuid, check if this nuid in student list.
def isValidNuid(student_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT nuid FROM student''')
    cursor.close()

    return student_id in cursor[0]


# Given student id, calculate the cumulative GPA that student have so far.
def calculateStudentGpa(student_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM registration WHERE (status = 'failed' OR status = 'completed') ''')
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


# The method takes student nuid as input,
def updateStudentGpa(student_id):
    cursor = connection.cursor()
    gpa = calculateStudentGpa(student_id)
    cursor.execute('''UPDATE student SET grade = %(gpa)s WHERE nuid = %(student_id)s ''',
                   {'gpa': gpa, 'student_id': student_id})
    cursor.close()


# Update all students GOA in the student list.
def updateAllStudentGpa():
    for s in getStudentIdList():
        updateStudentGpa(s)


# Registration Table
# Remove status equals 'rejected' rows form registration table.
def removeRejFromRegistration():
    cursor = connection.cursor()
    cursor.execute('''DELETE FROM registration WHERE status = 'rejected' ''')


# The methods takes a course numer, student id, return the status of the student for this course.
def getStudentCourseStatus(student_id, course_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT status FROM registration WHERE nuid = %(student_id)s AND
    course_id = %(course_id)s''', {'student_id': student_id, 'course_id': course_id})
    res = cursor.fetchall()
    cursor.close()

    if not res:
        return 'Null'
    elif res[0][0] == 'pending':
        return 'Pending for approval'

    return res[0][0]


# This method takes student nuid as input, return a course number list that contain courses the student currently
# taking or pending for advisor to approve.
def getCourseCurrentlyTakingOrPending(student_id):
    cursor = connection.cursor()
    res = []
    cursor.execute('''SELECT course_id FROM registration where nuid = %(student_id)s AND (status = 'approved' OR
    status = 'pending') ''', {'student_id': student_id})
    for c in cursor.fetchall():
        res.append(c[0])
    cursor.close()
    return res


# The method takes student nuid as input, return list that contain courses student currently taking.
def getCourseInProgress(student_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT course_id FROM registration WHERE nuid = %(student_id)s AND status = 'approved'
    ''', {'student_id': student_id})
    res = cursor.fetchall()
    cursor.close()

    if res:
        return res[0]

    return []


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


# Advisor Table
# The method takes student nuid as input, return student's advisor id.
def getAdvisorByStudentId(student_id):
    cursor = connection.cursor()
    student_id = {'student_id': student_id}
    cursor.execute('''SELECT advisor FROM student WHERE nuid = %(student_id)s''', student_id)
    cursor.close()
    return cursor.fetchall()[0][0]


# Admin Table


# Course Table
# Get course time by course id.
def getCourseTime(course_id):
    res = []
    cursor = connection.cursor()
    cursor.execute('''SELECT meeting_time FROM course WHERE course_id = %(course_id)s''', {'course_id': course_id})
    res.append(str(cursor.fetchall()[0][0]))
    cursor.execute('''SELECT date FROM course WHERE course_id = %(course_id)s''', {'course_id': course_id})
    if not cursor.fetchall():
        res.append(None)
    else:
        res.append(str(cursor.fetchall()[0][0]))
    cursor.close()

    return res
# The method takes course id as input, return if the course has reached it's capacity.
def isCourseFull(course_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT max_num_of_students FROM course WHERE course_id = %(course_id)s''',
                   {'course_id': course_id})
    cap = cursor.fetchall()[0][0]
    cursor.execute('''SELECT registered_num_of_stud FROM course WHERE course_id = %(course_id)s''',
                   {'course_id': course_id})
    cur_num = cursor.fetchall()[0][0]
    cursor.close()
    return cur_num >= cap


# Course Table
def getCourseNameByCourseNum(course_num):
    cursor = connection.cursor()
    cursor.execute('''SELECT course_name FROM course WHERE course_id = %(course_num)s''', {'course_num': course_num})
    res = cursor.fetchall()
    cursor.close()

    return res[0][0]


# Get all information from course table.
def getAllCourseInfo():
    cursor = connection.cursor()
    cursor.execute('''SELECT * FROM course''')
    res = cursor.fetchall()
    cursor.close()

    return res

# Get course number list.
def getCourseNumList():
    cursor = connection.cursor()
    cursor.execute('''SELECT course_id FROM course''')
    res = []

    for c in cursor.fetchall():
        res.append(c[0])
    cursor.close()

    return res

# Instructor Table
def getInstructorNameById(instructor_id):
    cursor = connection.cursor()
    cursor.execute('''SELECT name FROM instructor WHERE employee_id = %(employee_id)s ''',
                   {'employee_id': instructor_id})
    res = cursor.fetchall()

    if res:
        return res[0][0]

    return ""


# Util Library
def timeConversion(date, time):
    date_map = {'M': 1, 'T': 2, 'W': 3, 'Th': 4, 'F': 5, 'S': 6, 'S': 7}
    # Convert to seconds.
    one_day = 24 * 60
    hour = int(time[0 : 2])
    min = int(time[3 : 5])
    time_to_min = one_day - 1 * (date_map[date] - 1) + hour * 60 + min

    return time_to_min


def isConflict(student_id, course_id):
    course_time = getCourseTime(course_id)
    if course_time[1] == None:
        return False

    abs_course_time = timeConversion(course_time[1], course_time[0])
    reg_courses_time_interval = []

    for interval in getAllCourseInfo():
        if interval[0] == student_id and (interval[4] == 'pending' or interval[4] == 'approved'):
            ct = getCourseTime(interval[1])
            reg_courses_time_interval.append([ct, ct + 180])

    for ea in reg_courses_time_interval:
        if ea[0] < abs_course_time + 180 < ea[1] or ea[0] < abs_course_time < ea[1]:
            return False

    return True

def getGrade(grade):
    if grade < 1.0:
        return 'F'
    if grade == 1.0:
        return 'D'
    if grade <= 1.33:
        return 'D+'
    if grade <= 1.66:
        return 'C-+'
    if grade <= 2:
        return 'C'
    if grade <= 2.33:
        return 'C+'
    if grade <= 2.66:
        return 'B-'
    if grade <= 3:
        return 'B'
    if grade <= 3.33:
        return 'B+'
    if grade <= 3.66:
        return 'A-'

    return 'A'
