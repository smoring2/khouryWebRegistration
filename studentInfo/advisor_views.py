SQL_ADVISOR_INFO = '''SELECT * FROM advisor where employee_id = %(employee_id)s'''
SQL_ADVISOR_STU = '''SELECT * FROM student where advisor = %(employee_id)s'''
SQL_ADVISOR_STU_AVG_GPA = '''SELECT AVG(grade) FROM student GROUP BY advisor having advisor = %(employee_id)s'''
SQL_ADVISOR_STU_UNDER_3 = '''select * from student where advisor = %(employee_id)s and grade < 3'''
SQL_ADVISOR_STU_GAP_FULL = '''select * from student where advisor = %(employee_id)s and grade = 4'''
SQL_ADVISOR_STU_GPA_BETWEEN = '''select * from student  where advisor = %(employee_id)s and grade >= 3 AND grade < 4'''
SQL_REGISTRATIONS_STU_LIST = '''select nuid, course_id from registration where advisor_id = %(employee_id)s and pending is true'''
SQL_REGISTRATION_COMPLETED = '''select course_id from registration where nuid = %(nuid)s and completed is true'''
SQL_REGISTRATION_PENDING = '''select course_id from registration where nuid = %(nuid)s and pending is true'''
SQL_REGISTRATION_FAILED = '''select course_id from registration where nuid = %(nuid)s and failed is true'''
SQL_REGISTRATION_APPROVED = '''select course_id from registration where nuid = %(nuid)s and approved is true'''

from django.shortcuts import render
from django.db import connection
cursor= connection.cursor()

def getAdvisorProfile(request, employee_id):
    print("employee_id: " )
    val = {'employee_id': int(employee_id)}
    cursor.execute(SQL_ADVISOR_INFO, val)
    advisor_info = cursor.fetchall()
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

def getAdvisorStatistics(request, advisor_id):
    print("advisor_id: " )
    val = {'employee_id': int(advisor_id)}
    res = {}
    cursor.execute(SQL_ADVISOR_INFO, val)
    advisor_info = cursor.fetchall()
    res['advisor_name'] = advisor_info[0][1]
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
        res['numOfStus'] = len(stu_info[0])
        res['avg_gpa'] = stu_avg_gpa[0][0]
        res['numOfStusUnder'] = len(stu_gpa_under)
        res['numOfStusFull'] = len(stu_gpa_full)
        res['numOfStusBetween'] = len(stu_gpa_between)

    context = {
        "stuInfos": res
    }
    return render(request, 'advisor/advisor_index.html', context)


def getAdvisorRequests(request, advisor_id):
    val = {'employee_id': int(advisor_id)}
    results = {}
    cursor.execute(SQL_ADVISOR_INFO, val)
    advisor_info = cursor.fetchall()
    results['advisor_name'] = advisor_info[0][1]
    cursor.execute(SQL_REGISTRATIONS_STU_LIST, val)
    pendingList = cursor.fetchall()
    if pendingList:
        res = getStusPendingRegistration(pendingList)
    results['advisor_id'] = advisor_id
    results['pendings'] = res
    context = {
        "data" : results
    }
    return render(request, 'advisor/advisor_requests.html', context)


def getStusPendingRegistration(pendingList):
    SQL_STU_INFO = """select name, grade from student where nuid = %(nuid)s"""
    dict = {}
    for pending in pendingList:
        nuid = pending[0]
        course_id = pending[1]
        val = {'nuid' : int(nuid)}
        if nuid in dict:
            dict[nuid]["courses"].append(course_id)
            continue
        cursor.execute(SQL_STU_INFO, val)
        stu_info = cursor.fetchall()
        if stu_info:
            stu_name = stu_info[0][0]
            stu_grade = stu_info[0][1]
            dict[nuid] = {
                "nuid": nuid,
                "name": stu_name,
                'grade': stu_grade,
                "courses": [course_id],
            }
    results = []
    for key, vals in dict.items():
        results.append(vals)
    return results

def getAdvisorSearch(request, advisor_id):
    res = {}
    val = {'employee_id': int(advisor_id)}
    cursor.execute(SQL_ADVISOR_INFO, val)
    advisor_info = cursor.fetchall()
    res['advisor_name'] = advisor_info[0][1]
    res['advisor_id'] = advisor_id
    context = {
        "data": res
    }
    return render(request, 'advisor/advisor_search.html', context)

def getSearchDetails(request):
    nuid = request.GET.get('search')
    advisor_id = request.GET.get('advisor')
    val = {'employee_id': int(advisor_id)}
    cursor.execute(SQL_ADVISOR_INFO, val)
    advisor_info = cursor.fetchall()
    val = {'nuid': int(nuid)}
    details = {
        'advisor_id': advisor_id,
        'advisor_name': advisor_info[0][1],
        'pending_courses': [],
        'approved_courses': [],
        'completed_courses': [],
        'failed_courses': []
    }

    cursor.execute(SQL_REGISTRATION_PENDING, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            details['pending_courses'].append(r[0])

    cursor.execute(SQL_REGISTRATION_APPROVED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            details['approved_courses'].append(r[0])

    cursor.execute(SQL_REGISTRATION_COMPLETED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            details['completed_courses'].append(r[0])

    cursor.execute(SQL_REGISTRATION_FAILED, val)
    results = cursor.fetchall()
    if results:
        for r in results:
            details['failed_courses'].append(r[0])

    context = {
        "data": details
    }
    return render(request, 'advisor/advisor_search_details.html', context)



