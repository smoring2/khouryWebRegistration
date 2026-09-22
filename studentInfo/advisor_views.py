from django.http import Http404
from django.shortcuts import render
from django.db import connection

from .validation import coerce_int
SQL_ADVISOR_INFO = '''SELECT * FROM advisor where employee_id = %(employee_id)s'''
SQL_COURSE_INFO = '''SELECT * from course where course_id = %(course_id)s '''
SQL_STUDENT_INFO = '''select * from student where nuid = %(nuid)s '''
SQL_CAMPUS_INFO = '''Select * from campus where campusid = %(campusid)s'''
SQL_DEPARTMENT_INFO = '''Select * from department where department_id = %(department_id)s'''
SQL_COLLEGE_INFO = '''Select * from college where collegeid = %(collegeid)s'''
SQL_COURSE_DETAIL = '''select * from course where course_id = %(course_id)s '''

# cursor= connection.cursor()


def _fetch_by_id(sql, param_name, raw_id):
    """Run a single-id lookup after validating the id.

    Returns an empty list when the id is missing or not numeric, so callers can
    handle "not found" instead of propagating ``ValueError``/``TypeError``.
    """
    identifier = coerce_int(raw_id)
    if identifier is None:
        return []
    cursor = connection.cursor()
    try:
        cursor.execute(sql, {param_name: identifier})
        return cursor.fetchall()
    finally:
        cursor.close()


def getAdvisorInfoById(employee_id):
    return _fetch_by_id(SQL_ADVISOR_INFO, 'employee_id', employee_id)

def getCourseInfoByCourseId(course_id):
    return _fetch_by_id(SQL_COURSE_INFO, 'course_id', course_id)


def getStudentInfoByNuid(nuid):
    return _fetch_by_id(SQL_STUDENT_INFO, 'nuid', nuid)

def getDepartmentByDepartmentId(department_id):
    return _fetch_by_id(SQL_DEPARTMENT_INFO, 'department_id', department_id)

def getCampusByCampusId(campusid):
    return _fetch_by_id(SQL_CAMPUS_INFO, 'campusid', campusid)

def getCollegeByCollegeid(colleageid):
    return _fetch_by_id(SQL_COLLEGE_INFO, 'collegeid', colleageid)

SQL_INSTRUCTOR_INFO = '''select * from instructor where employee_id = %(instructor_id)s '''
def getInstructorByInstructorId(instructor_id):
    return _fetch_by_id(SQL_INSTRUCTOR_INFO, 'instructor_id', instructor_id)


def getAdvisorInfoOr404(advisor_id):
    """Return the advisor row or raise ``Http404``.

    Unknown or non-numeric ids must produce a clean 404 rather than an
    ``IndexError`` traceback.
    """
    advisor_info = getAdvisorInfoById(advisor_id)
    if not advisor_info:
        raise Http404('Advisor not found')
    return advisor_info


def getAdvisorProfile(request, employee_id):
    advisor_info = getAdvisorInfoOr404(employee_id)
    res = {}
    res['employee_id'] = employee_id
    res['name'] = advisor_info[0][1]
    res['email'] = advisor_info[0][2]
    res['phone'] = advisor_info[0][3]
    department_id = advisor_info[0][4]
    department_info = getDepartmentByDepartmentId(department_id)
    if department_info:
        res['department_id'] = department_info[0][0]
        res['department_name'] = department_info[0][1]
        res['office_addr'] = department_info[0][2]
    context = {
        "data": res
    }
    return render(request, 'advisor/advisor_profile.html', context)

SQL_ADVISOR_STU = '''SELECT * FROM student where advisor = %(employee_id)s'''
SQL_ADVISOR_STU_AVG_GPA = '''SELECT AVG(grade) FROM student GROUP BY advisor having advisor = %(employee_id)s'''
SQL_ADVISOR_STU_MAX_GPA = '''SELECT MAX(grade) FROM student GROUP BY advisor having advisor = %(employee_id)s'''
SQL_ADVISOR_STU_MIN_GPA = '''SELECT MIN(grade) FROM student GROUP BY advisor having advisor = %(employee_id)s'''
SQL_ADVISOR_STU_UNDER_3 = '''select * from student where advisor = %(employee_id)s and grade < 3'''
SQL_ADVISOR_STU_GAP_FULL = '''select * from student where advisor = %(employee_id)s and grade >= 4'''
SQL_ADVISOR_STU_GPA_BETWEEN = '''select * from student  where advisor = %(employee_id)s and grade >= 3 AND grade < 4'''

def getAdvisorStatistics(request, advisor_id):
    res = {}
    advisor_info = getAdvisorInfoOr404(advisor_id)
    res['advisor_id'] = advisor_id
    res['advisor_name'] = advisor_info[0][1]
    cursor= connection.cursor()
    val = {'employee_id': int(advisor_id)}
    cursor.execute(SQL_ADVISOR_STU, val)
    stu_info = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_AVG_GPA, val)
    stu_avg_gpa = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_MAX_GPA, val)
    stu_max_gpa = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_MIN_GPA, val)
    stu_min_gpa = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_UNDER_3, val)
    stu_gpa_under = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_GAP_FULL, val)
    stu_gpa_full = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_GPA_BETWEEN, val)
    stu_gpa_between = cursor.fetchall()

    if stu_info:
        res['numOfStus'] = len(stu_info)
        if stu_avg_gpa:
            res['avg_gpa'] = stu_avg_gpa[0][0]
        if stu_max_gpa:
            res['max_gpa'] = stu_max_gpa[0][0]
        if stu_min_gpa:
            res['min_gpa'] = stu_min_gpa[0][0]
        res['numOfStusUnder'] = len(stu_gpa_under)
        res['numOfStusFull'] = len(stu_gpa_full)
        res['numOfStusBetween'] = len(stu_gpa_between)

    context = {
        "stuInfos": res
    }
    cursor.close()
    return render(request, 'advisor/advisor_index.html', context)

SQL_REGISTRATIONS_STU_LIST = '''select nuid, course_id from registration where advisor_id = %(employee_id)s and status='pending' '''
def getAdvisorRequests(request, advisor_id):
    results = {}
    advisor_info = getAdvisorInfoOr404(advisor_id)
    results['advisor_name'] = advisor_info[0][1]
    cursor= connection.cursor()
    val = {'employee_id': int(advisor_id)}
    cursor.execute(SQL_REGISTRATIONS_STU_LIST, val)
    pendingList = cursor.fetchall()
    res =[]
    if pendingList:
        res = getStusPendingRegistration(pendingList)
    results['advisor_id'] = advisor_id
    results['pendings'] = res
    context = {
        "data" : results
    }
    cursor.close()
    return render(request, 'advisor/advisor_requests.html', context)

def getStusPendingRegistration(pendingList):
    dict = {}
    for pending in pendingList:
        nuid = pending[0]
        course_id = pending[1]
        course_info = getCourseInfoByCourseId(course_id)
        course_name = course_info[0][1] if course_info else ''
        if nuid in dict:
            dict[nuid]["courses"].append({'course_id': course_id, 'course_name': course_name})
            continue
        stu_info = getStudentInfoByNuid(nuid)
        if stu_info:
            stu_name = stu_info[0][1]
            stu_grade = stu_info[0][10]
            dict[nuid] = {
                "nuid": nuid,
                "name": stu_name,
                'grade': stu_grade,
                "courses": [{'course_id': course_id, 'course_name': course_name}],
            }
    results = []
    for key, vals in dict.items():
        results.append(vals)
    return results

def getAdvisorStudentSearch(request, advisor_id):
    res = {}
    advisor_info = getAdvisorInfoOr404(advisor_id)
    res['advisor_name'] = advisor_info[0][1]
    res['advisor_id'] = advisor_id
    context = {
        "data": res
    }
    return render(request, 'advisor/advisor_search.html', context)

SQL_REGISTRATION_COMPLETED = '''select course_id, grade from registration where nuid = %(nuid)s and status = 'completed' '''
SQL_REGISTRATION_PENDING = '''select course_id from registration where nuid = %(nuid)s and status = 'pending' '''
SQL_REGISTRATION_FAILED = '''select course_id, grade from registration where nuid = %(nuid)s and status = 'failed' '''
SQL_REGISTRATION_APPROVED = '''select course_id from registration where nuid = %(nuid)s and status = 'approved' '''
def getStudentSearchDetails(request):
    nuid = coerce_int(request.GET.get('nuid'))
    advisor_id = coerce_int(request.GET.get('advisor'))
    details = {
        'nuid': nuid,
        'advisor_id': advisor_id,
    }
    if advisor_id is None:
        raise Http404('Advisor not found')

    advisor_info = getAdvisorInfoOr404(advisor_id)
    student_info = getStudentInfoByNuid(nuid)
    if len(student_info) == 0:
        context = {
            'data': details
        }
        return render(request, 'advisor/advisor_search_details.html', context)

    stu_advisor_id = student_info[0][8]
    stu_advisor_info = getAdvisorInfoById(stu_advisor_id)
    campus_info = getCampusByCampusId(student_info[0][4])
    college_info = getCollegeByCollegeid(student_info[0][5])
    department_info = getDepartmentByDepartmentId(student_info[0][6])
    details = {
        'nuid': nuid,
        'student_name': student_info[0][1],
        'student_email': student_info[0][2],
        "student_grade": student_info[0][10],
        'student_campus': campus_info[0][1] if campus_info else '',
        'student_college': college_info[0][1] if college_info else '',
        'student_department': department_info[0][1] if department_info else '',
        'student_hours': student_info[0][11],
        'advisor_id': advisor_id,
        'advisor_name': advisor_info[0][1],
        'stu_advisor_id': stu_advisor_id,
        'stu_advisor_name': stu_advisor_info[0][1] if stu_advisor_info else '',
        'pending_courses': [],
        'approved_courses': [],
        'completed_courses': [],
        'failed_courses': []
    }
    cursor= connection.cursor()
    val = {'nuid': nuid}
    cursor.execute(SQL_REGISTRATION_PENDING, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            course_id = r[0]
            course_info = getCourseInfoByCourseId(r[0])
            if course_info:
                details['pending_courses'].append({'course_id':course_id, 'course_name':course_info[0][1]})

    cursor.execute(SQL_REGISTRATION_APPROVED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
             course_id = r[0]
             course_info = getCourseInfoByCourseId(r[0])
             if course_info:
                 details['approved_courses'].append({'course_id':course_id, 'course_name':course_info[0][1]})

    cursor.execute(SQL_REGISTRATION_COMPLETED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            course_id = r[0]
            course_info = getCourseInfoByCourseId(r[0])
            if course_info:
                details['completed_courses'].append({'course_id':course_id, 'course_name':course_info[0][1], 'course_gpa': r[1]})

    cursor.execute(SQL_REGISTRATION_FAILED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            course_id = r[0]
            course_info = getCourseInfoByCourseId(r[0])
            if course_info:
                details['failed_courses'].append({'course_id':course_id, 'course_name':course_info[0][1], 'course_gpa': r[1]})

    context = {
        "data": details
    }
    cursor.close()
    return render(request, 'advisor/advisor_search_details.html', context)

SQL_ADVISOR_STUS_LIST = '''select * from student where advisor = %(advisor)s '''
def getMyStudentsList(request, advisor_id):
    advisor_info = getAdvisorInfoOr404(advisor_id)
    cursor= connection.cursor()
    var = {'advisor': int(advisor_id)}
    cursor.execute(SQL_ADVISOR_STUS_LIST, var)
    students = cursor.fetchall()
    results = {
        'advisor_id': int(advisor_id),
        'advisor_name': advisor_info[0][1],
        'students': students
    }
    context = {
        "data": results
    }
    cursor.close()
    return render(request, 'advisor/advisor_students.html', context)

def getAdvisorCourseSearch(request, advisor_id):
    res = {}
    advisor_info = getAdvisorInfoOr404(advisor_id)
    res['advisor_name'] = advisor_info[0][1]
    res['advisor_id'] = advisor_id
    context = {
        "data": res
    }
    return render(request, 'advisor/advisor_courses.html', context)

SQL_COURSE_TAS = '''select * from ta where course_id = %(course_id)s '''
def getCourseSearchDetails(request):
     advisor_id = coerce_int(request.GET.get('advisor_id'))
     if advisor_id is None:
         raise Http404('Advisor not found')

     advisor_info = getAdvisorInfoOr404(advisor_id)
     results = {
        'advisor_id': advisor_id,
        'advisor_name': advisor_info[0][1],
     }
     course_id = coerce_int(request.GET.get('course_id'))
     results['course_id'] = course_id
     course_info = getCourseInfoByCourseId(course_id)
     if len(course_info) == 0:
        context = {
            'data': results
        }
        return render(request, 'advisor/advisor_course_details.html', context)

     results['course_name'] = course_info[0][1]
     results['instructor_id'] = course_info[0][2]
     results['meeting_time'] = course_info[0][3]
     results['max_num_of_students'] = course_info[0][4]
     results['semester'] = course_info[0][5]
     results['semester_hrs'] = course_info[0][6]
     results['registered_num_of_stud'] = course_info[0][7]
     results['department_id'] = course_info[0][8]
     results['campusid'] = course_info[0][9]
     results['building_id'] = course_info[0][10]
     results['room_id'] = course_info[0][11]
     instructor_id = course_info[0][2]
     instructor_info = getInstructorByInstructorId(instructor_id)
     results['instructor_name'] = instructor_info[0][3] if instructor_info else ''
     val = {'course_id': course_id}
     cursor = connection.cursor()
     cursor.execute(SQL_COURSE_TAS, val)
     tas = cursor.fetchall()
     results['tas'] = tas
     cursor.close()
     context = {
        'data': results
     }
     return render(request, 'advisor/advisor_course_details.html', context)
