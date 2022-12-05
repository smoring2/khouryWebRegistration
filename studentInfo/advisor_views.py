from django.shortcuts import render
from django.db import connection
SQL_ADVISOR_INFO = '''SELECT * FROM advisor where employee_id = %(employee_id)s'''
SQL_COURSE_INFO = '''SELECT * from course where course_id = %(course_id)s '''
SQL_STUDENT_INFO = '''select * from student where nuid = %(nuid)s '''
SQL_CAMPUS_INFO = '''Select * from campus where campusid = %(campusid)s'''
SQL_DEPARTMENT_INFO = '''Select * from department where department_id = %(department_id)s'''
SQL_COLLEGE_INFO = '''Select * from college where collegeid = %(collegeid)s'''
# cursor= connection.cursor()

def getAdvisorInfoById(employee_id):
    cursor= connection.cursor()
    val = {'employee_id': int(employee_id)}
    cursor.execute(SQL_ADVISOR_INFO, val)
    try:
        advisor_info = cursor.fetchall()
    except Exception as e:
        print("error")
        print(e)
    cursor.close()
    return advisor_info

def getCourseInfoByCourseId(course_id):
    cursor= connection.cursor()
    val = {'course_id': int(course_id)}
    cursor.execute(SQL_COURSE_INFO, val)
    course_info = cursor.fetchall()
    cursor.close()
    return course_info


def getStudentInfoByNuid(nuid):
    cursor = connection.cursor()
    val = {'nuid': int(nuid)}
    cursor.execute(SQL_STUDENT_INFO, val)
    student_info = cursor.fetchall()
    cursor.close()
    return student_info

def getDepartmentByDepartmentId(department_id):
    cursor = connection.cursor()
    val = {'department_id': int(department_id)}
    cursor.execute(SQL_DEPARTMENT_INFO, val)
    department_info = cursor.fetchall()
    cursor.close()
    return department_info

def getCampusByCampusId(campusid):
    cursor = connection.cursor()
    val = {'campusid': int(campusid)}
    cursor.execute(SQL_CAMPUS_INFO, val)
    campus_info = cursor.fetchall()
    cursor.close()
    return campus_info

def getCollegeByCollegeid(colleageid):
    cursor = connection.cursor()
    val = {'collegeid': int(colleageid)}
    cursor.execute(SQL_COLLEGE_INFO, val)
    college_info = cursor.fetchall()
    cursor.close()
    return college_info

def getAdvisorProfile(request, employee_id):
    advisor_info = getAdvisorInfoById(employee_id)
    res = {}
    if advisor_info:
        res['employee_id'] = employee_id
        res['name'] = advisor_info[0][1]
        res['email'] = advisor_info[0][2]
        res['phone'] = advisor_info[0][3]

    context = {
        "data": res
    }
    return render(request, 'advisor/advisor_profile.html', context)

SQL_ADVISOR_STU = '''SELECT * FROM student where advisor = %(employee_id)s'''
SQL_ADVISOR_STU_AVG_GPA = '''SELECT AVG(grade) FROM student GROUP BY advisor having advisor = %(employee_id)s'''
SQL_ADVISOR_STU_UNDER_3 = '''select * from student where advisor = %(employee_id)s and grade < 3'''
SQL_ADVISOR_STU_GAP_FULL = '''select * from student where advisor = %(employee_id)s and grade >= 4'''
SQL_ADVISOR_STU_GPA_BETWEEN = '''select * from student  where advisor = %(employee_id)s and grade >= 3 AND grade < 4'''

def getAdvisorStatistics(request, advisor_id):
    res = {}
    advisor_info = getAdvisorInfoById(advisor_id)
    res['advisor_name'] = advisor_info[0][1]
    cursor= connection.cursor()
    val = {'employee_id': int(advisor_id)}
    cursor.execute(SQL_ADVISOR_STU, val)
    stu_info = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_AVG_GPA, val)
    stu_avg_gpa = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_UNDER_3, val)
    stu_gpa_under = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_GAP_FULL, val)
    stu_gpa_full = cursor.fetchall()
    cursor.execute(SQL_ADVISOR_STU_GPA_BETWEEN, val)
    stu_gpa_between = cursor.fetchall()

    if stu_info:
        res['advisor_id'] = advisor_id
        res['numOfStus'] = len(stu_info)
        res['avg_gpa'] = stu_avg_gpa[0][0]
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
    advisor_info = getAdvisorInfoById(advisor_id)
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
        course_name = getCourseInfoByCourseId(course_id)[0][1]
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

def getAdvisorSearch(request, advisor_id):
    res = {}
    val = {'employee_id': int(advisor_id)}
    advisor_info = getAdvisorInfoById(advisor_id)
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
def getSearchDetails(request):
    nuid = request.GET.get('search')
    advisor_id = request.GET.get('advisor')
    advisor_info = getAdvisorInfoById(advisor_id)
    student_info = getStudentInfoByNuid(nuid)
    campus_info = getCampusByCampusId(student_info[0][4])
    college_info = getCollegeByCollegeid(student_info[0][5])
    department_info = getDepartmentByDepartmentId(student_info[0][6])
    details = {
        'nuid': nuid,
        'student_name': student_info[0][1],
        'student_email': student_info[0][2],
        "student_grade": student_info[0][10],
        'student_campus': campus_info[0][1],
        'student_college': college_info[0][1],
        'student_department': department_info[0][1],
        'student_hours': student_info[0][11],
        'advisor_id': advisor_id,
        'advisor_name': advisor_info[0][1],
        'pending_courses': [],
        'approved_courses': [],
        'completed_courses': [],
        'failed_courses': []
    }
    cursor= connection.cursor()
    val = {'nuid': int(nuid)}
    cursor.execute(SQL_REGISTRATION_PENDING, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            course_id = r[0]
            course_info = getCourseInfoByCourseId(r[0])
            details['pending_courses'].append({'course_id':course_id, 'course_name':course_info[0][1]})

    cursor.execute(SQL_REGISTRATION_APPROVED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
             course_id = r[0]
             course_info = getCourseInfoByCourseId(r[0])
             details['approved_courses'].append({'course_id':course_id, 'course_name':course_info[0][1]})

    cursor.execute(SQL_REGISTRATION_COMPLETED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            course_id = r[0]
            course_info = getCourseInfoByCourseId(r[0])
            details['completed_courses'].append({'course_id':course_id, 'course_name':course_info[0][1], 'course_gpa': r[1]})

    cursor.execute(SQL_REGISTRATION_FAILED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            course_id = r[0]
            course_info = getCourseInfoByCourseId(r[0])
            details['failed_courses'].append({'course_id':course_id, 'course_name':course_info[0][1], 'course_gpa': r[1]})

    context = {
        "data": details
    }
    cursor.close()
    return render(request, 'advisor/advisor_search_details.html', context)

SQL_ADVISOR_STUS_LIST = '''select * from student where advisor = %(advisor)s '''
def getMyStudentsList(request, advisor_id):
    cursor= connection.cursor()
    var = {'advisor': int(advisor_id)}
    cursor.execute(SQL_ADVISOR_STUS_LIST, var)
    students = cursor.fetchall()
    advisor_info = getAdvisorInfoById(advisor_id)
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





