from django.http import Http404
from django.shortcuts import render
from django.db import connection

from .validators import (InvalidParameter, first_row, get_int,
                         get_str, html_bad_request_guard, to_int)

SQL_ADVISOR_INFO = '''SELECT * FROM advisor where employee_id = %(employee_id)s'''
SQL_COURSE_INFO = '''SELECT * from course where course_id = %(course_id)s '''
SQL_STUDENT_INFO = '''select * from student where nuid = %(nuid)s '''
SQL_CAMPUS_INFO = '''Select * from campus where campusid = %(campusid)s'''
SQL_DEPARTMENT_INFO = '''Select * from department where department_id = %(department_id)s'''
SQL_COLLEGE_INFO = '''Select * from college where collegeid = %(collegeid)s'''
SQL_COURSE_DETAIL = '''select * from course where course_id = %(course_id)s '''

ADVISOR_NOT_FOUND = 'No advisor matches the given id.'

# cursor= connection.cursor()

def _fetch_one_column_set(sql, params):
    """Run a lookup query and always return a (possibly empty) result set."""
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()

def getAdvisorInfoById(employee_id):
    val = {'employee_id': to_int(employee_id, 'employee_id')}
    return _fetch_one_column_set(SQL_ADVISOR_INFO, val)

def getCourseInfoByCourseId(course_id):
    val = {'course_id': to_int(course_id, 'course_id')}
    return _fetch_one_column_set(SQL_COURSE_INFO, val)


def getStudentInfoByNuid(nuid):
    val = {'nuid': to_int(nuid, 'nuid')}
    return _fetch_one_column_set(SQL_STUDENT_INFO, val)

def getDepartmentByDepartmentId(department_id):
    val = {'department_id': to_int(department_id, 'department_id')}
    return _fetch_one_column_set(SQL_DEPARTMENT_INFO, val)

def getCampusByCampusId(campusid):
    val = {'campusid': to_int(campusid, 'campusid')}
    return _fetch_one_column_set(SQL_CAMPUS_INFO, val)

def getCollegeByCollegeid(colleageid):
    val = {'collegeid': to_int(colleageid, 'collegeid')}
    return _fetch_one_column_set(SQL_COLLEGE_INFO, val)

SQL_INSTRUCTOR_INFO = '''select * from instructor where employee_id = %(instructor_id)s '''
def getInstructorByInstructorId(instructor_id):
    val = {'instructor_id': to_int(instructor_id, 'instructor_id')}
    return _fetch_one_column_set(SQL_INSTRUCTOR_INFO, val)

def getAdvisorRowOr404(advisor_id):
    """Return the advisor row, or raise ``Http404`` when the id is unknown.

    Indexing ``advisor_info[0]`` without this check raises ``IndexError`` for any
    non-existent id, which Django renders as a debug traceback.
    """
    advisor_row = first_row(getAdvisorInfoById(advisor_id))
    if advisor_row is None:
        raise Http404(ADVISOR_NOT_FOUND)
    return advisor_row

@html_bad_request_guard
def getAdvisorProfile(request, employee_id):
    advisor_row = getAdvisorRowOr404(employee_id)
    res = {
        'employee_id': employee_id,
        'name': advisor_row[1],
        'email': advisor_row[2],
        'phone': advisor_row[3],
    }
    department_id = advisor_row[4]
    if department_id is not None:
        department_row = first_row(getDepartmentByDepartmentId(department_id))
        if department_row is not None:
            res['department_id'] = department_row[0]
            res['department_name'] = department_row[1]
            res['office_addr'] = department_row[2]
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

@html_bad_request_guard
def getAdvisorStatistics(request, advisor_id):
    res = {}
    advisor_row = getAdvisorRowOr404(advisor_id)
    res['advisor_id'] = advisor_id
    res['advisor_name'] = advisor_row[1]
    cursor= connection.cursor()
    try:
        val = {'employee_id': to_int(advisor_id, 'advisor_id')}
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
    finally:
        cursor.close()

    if stu_info:
        res['numOfStus'] = len(stu_info)
        avg_row = first_row(stu_avg_gpa)
        max_row = first_row(stu_max_gpa)
        min_row = first_row(stu_min_gpa)
        res['avg_gpa'] = avg_row[0] if avg_row else None
        res['max_gpa'] = max_row[0] if max_row else None
        res['min_gpa'] = min_row[0] if min_row else None
        res['numOfStusUnder'] = len(stu_gpa_under)
        res['numOfStusFull'] = len(stu_gpa_full)
        res['numOfStusBetween'] = len(stu_gpa_between)

    context = {
        "stuInfos": res
    }
    return render(request, 'advisor/advisor_index.html', context)

SQL_REGISTRATIONS_STU_LIST = '''select nuid, course_id from registration where advisor_id = %(employee_id)s and status='pending' '''
@html_bad_request_guard
def getAdvisorRequests(request, advisor_id):
    results = {}
    advisor_row = getAdvisorRowOr404(advisor_id)
    results['advisor_name'] = advisor_row[1]
    cursor= connection.cursor()
    try:
        val = {'employee_id': to_int(advisor_id, 'advisor_id')}
        cursor.execute(SQL_REGISTRATIONS_STU_LIST, val)
        pendingList = cursor.fetchall()
    finally:
        cursor.close()
    res =[]
    if pendingList:
        res = getStusPendingRegistration(pendingList)
    results['advisor_id'] = advisor_id
    results['pendings'] = res
    context = {
        "data" : results
    }
    return render(request, 'advisor/advisor_requests.html', context)

def getStusPendingRegistration(pendingList):
    dict = {}
    for pending in pendingList:
        nuid = pending[0]
        course_id = pending[1]
        course_row = first_row(getCourseInfoByCourseId(course_id))
        course_name = course_row[1] if course_row else ''
        if nuid in dict:
            dict[nuid]["courses"].append({'course_id': course_id, 'course_name': course_name})
            continue
        stu_row = first_row(getStudentInfoByNuid(nuid))
        if stu_row is not None:
            stu_name = stu_row[1]
            stu_grade = stu_row[10]
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

@html_bad_request_guard
def getAdvisorStudentSearch(request, advisor_id):
    res = {}
    advisor_row = getAdvisorRowOr404(advisor_id)
    res['advisor_name'] = advisor_row[1]
    res['advisor_id'] = advisor_id
    context = {
        "data": res
    }
    return render(request, 'advisor/advisor_search.html', context)

SQL_REGISTRATION_COMPLETED = '''select course_id, grade from registration where nuid = %(nuid)s and status = 'completed' '''
SQL_REGISTRATION_PENDING = '''select course_id from registration where nuid = %(nuid)s and status = 'pending' '''
SQL_REGISTRATION_FAILED = '''select course_id, grade from registration where nuid = %(nuid)s and status = 'failed' '''
SQL_REGISTRATION_APPROVED = '''select course_id from registration where nuid = %(nuid)s and status = 'approved' '''
@html_bad_request_guard
def getStudentSearchDetails(request):
    # The nuid comes from a free-text search box, so a non-numeric term is
    # treated as "no match" rather than an error.
    raw_nuid = get_str(request.GET, 'nuid')
    advisor_id = get_int(request.GET, 'advisor')
    details = {
        'nuid': raw_nuid,
        'advisor_id': advisor_id,
    }
    advisor_row = getAdvisorRowOr404(advisor_id)
    try:
        nuid = to_int(raw_nuid, 'nuid')
        student_row = first_row(getStudentInfoByNuid(nuid))
    except InvalidParameter:
        student_row = None
    if student_row is None:
        context = {
            'data': details
        }
        return render(request, 'advisor/advisor_search_details.html', context)

    stu_advisor_id = student_row[8]
    stu_advisor_row = first_row(getAdvisorInfoById(stu_advisor_id)) if stu_advisor_id is not None else None
    campus_row = first_row(getCampusByCampusId(student_row[4])) if student_row[4] is not None else None
    college_row = first_row(getCollegeByCollegeid(student_row[5])) if student_row[5] is not None else None
    department_row = first_row(getDepartmentByDepartmentId(student_row[6])) if student_row[6] is not None else None
    details = {
        'nuid': nuid,
        'student_name': student_row[1],
        'student_email': student_row[2],
        "student_grade": student_row[10],
        'student_campus': campus_row[1] if campus_row else '',
        'student_college': college_row[1] if college_row else '',
        'student_department': department_row[1] if department_row else '',
        'student_hours': student_row[11],
        'advisor_id': advisor_id,
        'advisor_name': advisor_row[1],
        'stu_advisor_id': stu_advisor_id,
        'stu_advisor_name': stu_advisor_row[1] if stu_advisor_row else '',
        'pending_courses': [],
        'approved_courses': [],
        'completed_courses': [],
        'failed_courses': []
    }
    cursor= connection.cursor()
    try:
        val = {'nuid': nuid}
        cursor.execute(SQL_REGISTRATION_PENDING, val)
        results = cursor.fetchall()
        if results:
            for r in results:
                course_id = r[0]
                course_row = first_row(getCourseInfoByCourseId(course_id))
                details['pending_courses'].append({'course_id':course_id, 'course_name':course_row[1] if course_row else ''})

        cursor.execute(SQL_REGISTRATION_APPROVED, val)
        results = cursor.fetchall()
        if results:
            for r in results:
                course_id = r[0]
                course_row = first_row(getCourseInfoByCourseId(course_id))
                details['approved_courses'].append({'course_id':course_id, 'course_name':course_row[1] if course_row else ''})

        cursor.execute(SQL_REGISTRATION_COMPLETED, val)
        results = cursor.fetchall()
        if results:
            for r in results:
                course_id = r[0]
                course_row = first_row(getCourseInfoByCourseId(course_id))
                details['completed_courses'].append({'course_id':course_id, 'course_name':course_row[1] if course_row else '', 'course_gpa': r[1]})

        cursor.execute(SQL_REGISTRATION_FAILED, val)
        results = cursor.fetchall()
        if results:
            for r in results:
                course_id = r[0]
                course_row = first_row(getCourseInfoByCourseId(course_id))
                details['failed_courses'].append({'course_id':course_id, 'course_name':course_row[1] if course_row else '', 'course_gpa': r[1]})
    finally:
        cursor.close()

    context = {
        "data": details
    }
    return render(request, 'advisor/advisor_search_details.html', context)

SQL_ADVISOR_STUS_LIST = '''select * from student where advisor = %(advisor)s '''
@html_bad_request_guard
def getMyStudentsList(request, advisor_id):
    advisor_row = getAdvisorRowOr404(advisor_id)
    cursor= connection.cursor()
    try:
        var = {'advisor': to_int(advisor_id, 'advisor_id')}
        cursor.execute(SQL_ADVISOR_STUS_LIST, var)
        students = cursor.fetchall()
    finally:
        cursor.close()
    results = {
        'advisor_id': to_int(advisor_id, 'advisor_id'),
        'advisor_name': advisor_row[1],
        'students': students
    }
    context = {
        "data": results
    }
    return render(request, 'advisor/advisor_students.html', context)

@html_bad_request_guard
def getAdvisorCourseSearch(request, advisor_id):
    res = {}
    advisor_row = getAdvisorRowOr404(advisor_id)
    res['advisor_name'] = advisor_row[1]
    res['advisor_id'] = advisor_id
    context = {
        "data": res
    }
    return render(request, 'advisor/advisor_courses.html', context)

SQL_COURSE_TAS = '''select * from ta where course_id = %(course_id)s '''
@html_bad_request_guard
def getCourseSearchDetails(request):
     advisor_id = get_int(request.GET, 'advisor_id')
     advisor_row = getAdvisorRowOr404(advisor_id)
     results = {
        'advisor_id': advisor_id,
        'advisor_name': advisor_row[1],
     }
     # The course id comes from a free-text search box; a non-numeric term is
     # treated as "no match" rather than an error.  Only the numeric form is
     # published as 'course_id' because the template interpolates it into
     # JavaScript; the raw term is echoed back separately as plain text.
     raw_course_id = get_str(request.GET, 'course_id')
     results['course_query'] = raw_course_id
     course_id = 0
     try:
        course_id = to_int(raw_course_id, 'course_id')
        course_row = first_row(getCourseInfoByCourseId(course_id))
     except InvalidParameter:
        course_row = None
     results['course_id'] = course_id
     if course_row is None:
        context = {
            'data': results
        }
        return render(request, 'advisor/advisor_course_details.html', context)

     results['course_name'] = course_row[1]
     results['instructor_id'] = course_row[2]
     results['meeting_time'] = course_row[3]
     results['max_num_of_students'] = course_row[4]
     results['semester'] = course_row[5]
     results['semester_hrs'] = course_row[6]
     results['registered_num_of_stud'] = course_row[7]
     results['department_id'] = course_row[8]
     results['campusid'] = course_row[9]
     results['building_id'] = course_row[10]
     results['room_id'] = course_row[11]
     instructor_id = course_row[2]
     instructor_row = first_row(getInstructorByInstructorId(instructor_id)) if instructor_id is not None else None
     results['instructor_name'] = instructor_row[3] if instructor_row else ''
     cursor = connection.cursor()
     try:
        cursor.execute(SQL_COURSE_TAS, {'course_id': course_id})
        tas = cursor.fetchall()
     finally:
        cursor.close()
     results['tas'] = tas
     context = {
        'data': results
     }
     return render(request, 'advisor/advisor_course_details.html', context)
