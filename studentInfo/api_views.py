from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from django.db import connection

from .validation import (coerce_float, coerce_int, collect_ints, get_text,
                         invalid_parameters_message)
NO_PERMISSION_ALERT = "No records.\n Or No permission. This is not your student!"
SUCCEED_ALERT = "Succeed"
ERROR_ALERT = "Something wrong! Please try again!"
INVALID_REQUEST_ALERT = "Invalid request parameters."


def invalid_params_response(invalid, extra=None):
    """Return a 400 JSON response naming the rejected parameters.

    Query parameters must be validated before they are cast, otherwise a
    missing or non-numeric value raises ``TypeError``/``ValueError``.  DRF's
    exception handler does not convert those, so they reach Django and render
    the technical 500 page (source, frame locals, SQL, settings).
    """
    payload = {'message': invalid_parameters_message(invalid)}
    if extra:
        payload.update(extra)
    return JsonResponse(payload, safe=False, status=400)


SQL_COURSE_ADD_NUM = '''update course set registered_num_of_stud = registered_num_of_stud + 1 where course_id = %(course_id)s '''
SQL_COURSE_INFO = '''select * from course where course_id = %(course_id)s '''
SQL_REGISTRATION_APPROVAL = '''update registration set status = 'approved'
where nuid = %(nuid)s and status = 'pending' and advisor_id = %(advisor_id)s '''
SQL_REGISTRATION_PENDING_LIST = '''select * from registration where nuid = %(nuid)s and status = 'pending' and advisor_id = %(advisor_id)s'''
@api_view(['GET'])
def approvePendingRequest(request):
    params, invalid = collect_ints(request.query_params, 'nuid', 'advisor_id')
    if invalid:
        return invalid_params_response(invalid)
    nuid = params['nuid']
    advisor_id = params['advisor_id']
    val = {'nuid': nuid, 'advisor_id': advisor_id}
    message= ""
    try:
        cursor= connection.cursor()
        cursor.execute(SQL_REGISTRATION_PENDING_LIST, val)
        course_list = cursor.fetchall()
        cursor.close()
        if course_list:
            for c in course_list:
                c_id = c[1]
                m = addApprovedCourse(nuid, c_id, advisor_id)
                message = message + m + "\n"
        else:
            message = NO_PERMISSION_ALERT
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    return JsonResponse({"message": message}, safe=False)

SQL_REGISTRATION_REJECTION = '''update registration set status = 'rejected'
where nuid= %(nuid)s and advisor_id = %(advisor_id)s and ( status = 'pending' or status ='approved') '''
SQL_PENDING_REJECTION = '''delete from registration where nuid= %(nuid)s and advisor_id = %(advisor_id)s and status = 'pending' '''
@api_view(['GET'])
def rejectPendingRequest(request):
    params, invalid = collect_ints(request.query_params, 'nuid', 'advisor_id')
    if invalid:
        return invalid_params_response(invalid)
    cursor= connection.cursor()
    val = {'nuid': params['nuid'], 'advisor_id': params['advisor_id']}
    message="succeed"
    try:
        cursor.execute(SQL_PENDING_REJECTION, val)
        counts = cursor.rowcount
        if counts == 0:
            message = NO_PERMISSION_ALERT
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({"message": message}, safe=False)


SQL_REGISTRATION_REMOVE = '''update registration set status = 'rejected'
where nuid= %(nuid)s and course_id = %(course_id)s and advisor_id = %(advisor_id)s'''
SQL_APPROVED_REJECTION = '''delete from registration where nuid= %(nuid)s and advisor_id = %(advisor_id)s and course_id = %(course_id)s and status = 'approved' '''
SQL_REGISTERED_NUM_MINUS = '''update course set registered_num_of_stud = registered_num_of_stud - 1 where course_id = %(course_id)s '''
@api_view(['GET'])
def removeOneApprovedCourse(request):
    params, invalid = collect_ints(request.query_params, 'nuid', 'course_id', 'advisor_id')
    if invalid:
        return invalid_params_response(invalid)
    val = {'nuid': params['nuid'], 'course_id': params['course_id'], 'advisor_id': params['advisor_id']}
    cursor= connection.cursor()
    message = ""
    try:
        cursor.execute(SQL_APPROVED_REJECTION, val)
        counts = cursor.rowcount
        if counts == 0:
            message = NO_PERMISSION_ALERT
        else:
            cursor.execute(SQL_REGISTERED_NUM_MINUS, val)
            message = SUCCEED_ALERT
    except:
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message}, safe=False)

SQL_REGISTRATION_INFO = '''select * from registration
where nuid= %(nuid)s and course_id = %(course_id)s and advisor_id = %(advisor_id)s '''
SQL_REGISTRATION_ADD = '''update registration set status = 'approved'
where nuid= %(nuid)s and course_id = %(course_id)s and advisor_id = %(advisor_id)s'''
SQL_REGISTRATION_INSERT = '''insert into registration values
(%(nuid)s, %(course_id)s, %(advisor_id)s, null, 'approved')'''
@api_view(['GET'])
def addOneApprovedCourse(request):
    params, invalid = collect_ints(request.query_params, 'nuid', 'course_id', 'advisor_id')
    if invalid:
        return invalid_params_response(invalid)
    message = addApprovedCourse(params['nuid'], params['course_id'], params['advisor_id'])
    return JsonResponse({'message': message}, safe=False)

def addApprovedCourse(nuid, course_id, advisor_id):
    print('addApprovedCourse')
    nuid = coerce_int(nuid)
    course_id = coerce_int(course_id)
    advisor_id = coerce_int(advisor_id)
    if nuid is None or course_id is None or advisor_id is None:
        return INVALID_REQUEST_ALERT
    cursor= connection.cursor()
    val = {'nuid': nuid, 'course_id': course_id, 'advisor_id': advisor_id}
    message = str(course_id) + " added successfully"
    cursor.execute('''SElect * from student where nuid = %(nuid)s ''', {'nuid': nuid})
    student_info = cursor.fetchall()
    if student_info:
        stu_advisor = coerce_int(student_info[0][8])
        print(stu_advisor)
        if stu_advisor == advisor_id:
            try:
                cursor.execute(SQL_REGISTRATION_INFO, val)
                registration_info = cursor.fetchall()
                if len(registration_info) > 0 and (registration_info[0][4] == 'completed' or registration_info[0][4] == 'failed'):
                    message = "Student already has taken this course"
                else:
                    cursor.execute(SQL_COURSE_INFO, val)
                    c_info = cursor.fetchall()
                    print(c_info)
                    if c_info:
                        max_num_of_stus = coerce_int(c_info[0][4], 0)
                        reg_num_of_stus = coerce_int(c_info[0][7], 0)
                        if max_num_of_stus > reg_num_of_stus:
                            if registration_info:
                                cursor.execute(SQL_REGISTRATION_ADD, val)
                            else:
                                cursor.execute(SQL_REGISTRATION_INSERT, val)
                            cursor.execute(SQL_COURSE_ADD_NUM, val)
                        else:
                            message="This course " + str(course_id) + " is full!"
                    else:
                        message = str(course_id) + " not found"
            except Exception as e:
                print(e)
                message = "Something wrong with "  +  str(course_id) + "! Please try again"
        else:
            message = NO_PERMISSION_ALERT
    else:
        message = NO_PERMISSION_ALERT
    cursor.close()
    print(message)
    return message


SQL_REGISTRATION_UPDATE_GPA = '''update registration set grade = %(grade)s where nuid= %(nuid)s and course_id = %(course_id)s and advisor_id = %(advisor_id)s '''
SQL_STUDENT_GPA_UPDATE = '''update student set grade = %(grade)s where nuid = %(nuid)s '''
SQL_STUDENT_GPA_CAL = '''SELECT avg(grade) from registration where grade is not null
group by nuid having nuid = %(nuid)s'''
@api_view(['GET'])
def updateGPA(request):
    params, invalid = collect_ints(request.query_params, 'nuid', 'course_id', 'advisor_id')
    grade = coerce_float(request.query_params.get('grade'))
    if grade is None:
        invalid = invalid + ['grade']
    if invalid:
        return invalid_params_response(invalid)
    nuid = params['nuid']
    cursor= connection.cursor()
    val = {'nuid': nuid, 'course_id': params['course_id'], 'advisor_id': params['advisor_id'], 'grade': grade}
    message = "succeed"
    try:
        cursor.execute(SQL_REGISTRATION_UPDATE_GPA, val)
        counts = cursor.rowcount
        print(counts)
        if counts ==  0:
            message = NO_PERMISSION_ALERT
        else:
            cursor.execute(SQL_STUDENT_GPA_CAL, val)
            gpas = cursor.fetchall()
            curr_gpa = coerce_float(gpas[0][0]) if gpas else None
            if curr_gpa is not None:
                val = {'grade': curr_gpa, 'nuid' : nuid}
                cursor.execute(SQL_STUDENT_GPA_UPDATE, val)
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message}, safe=False)


SQL_STUDENT_INSERT = ''' insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, semesterhour, password) values (%(nuid)s, %(name)s, %(email)s,  %(bdate)s, %(campus)s, %(college)s, %(department)s, %(phone)s, %(advisor)s, 8, %(password)s) '''
SQL_NUID_CHECK = '''select * from student where nuid = %(nuid)s '''
@api_view(['GET'])
def insertStudent(request):
    nuid = coerce_int(request.query_params.get('nuid'))
    if nuid is None:
        return invalid_params_response(['nuid'], {'succeed': 0})

    cursor= connection.cursor()
    message = SUCCEED_ALERT
    succeed = 0
    try:
        cursor.execute(SQL_NUID_CHECK, {'nuid': nuid})
        res = cursor.fetchall()
    except Exception as e:
        print(e)
        cursor.close()
        return JsonResponse({'message': ERROR_ALERT, "succeed": 0}, safe=False)

    if res:
        cursor.close()
        message = "This NUID has been taken. Please use choose different one"
        return JsonResponse({'message': message, "succeed": 0}, safe=False)

    val = {
        'nuid' : nuid,
        'name': get_text(request.query_params, 'name'),
        'email': get_text(request.query_params, 'email'),
        'bdate': get_text(request.query_params, 'bdate'),
        'campus': coerce_int(request.query_params.get('campus')),
        'college': coerce_int(request.query_params.get('college')),
        'department': coerce_int(request.query_params.get('department')),
        'phone': get_text(request.query_params, 'phone'),
        'advisor': coerce_int(request.query_params.get('advisor_id')),
        'password': request.query_params.get('password') or ''
    }
    try:
        cursor.execute(SQL_STUDENT_INSERT, val)
        succeed = 1
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message, "succeed": succeed}, safe=False)

SQL_STUDENT_UPDATE_HOURS = '''update student set semesterhour= %(hours)s where nuid = %(nuid)s '''
@api_view(['GET'])
def updateHours(request):
    params, invalid = collect_ints(request.query_params, 'nuid', 'hours')
    if invalid:
        return invalid_params_response(invalid)
    cursor= connection.cursor()
    val = {'nuid': params['nuid'], 'hours': params['hours']}
    message = ''
    try:
        cursor.execute(SQL_STUDENT_UPDATE_HOURS, val)
        message = SUCCEED_ALERT
    except:
        message = ERROR_ALERT
    cursor.close()
    print(message)
    return JsonResponse({'message': message}, safe=False)


SQL_ADVISOR_UPDATE_PHONE = '''update advisor set phone = %(phone)s where employee_id = %(advisor_id)s '''
@api_view(['GET'])
def updatePhone(request):
    params, invalid = collect_ints(request.query_params, 'advisor_id', 'phone')
    if invalid:
        return invalid_params_response(invalid)
    cursor= connection.cursor()
    val = {'advisor_id': params['advisor_id'], 'phone': params['phone']}
    message = SUCCEED_ALERT
    try:
        cursor.execute(SQL_ADVISOR_UPDATE_PHONE, val)
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message}, safe=False)

SQL_COURSE_ROOM = '''update course set campusid = %(campusid)s,
building_id = %(building_id)s, room_id = %(room_id)s where course_id = %(course_id)s '''
@api_view(['GET'])
def saveClassRoom(request):
    params, invalid = collect_ints(request.query_params, 'course_id', 'campusid', 'building_id', 'room_id')
    if invalid:
        return invalid_params_response(invalid)
    val = {'course_id': params['course_id'], 'campusid': params['campusid'],
           'building_id': params['building_id'], 'room_id': params['room_id']}
    cursor = connection.cursor()
    message = ''
    try:
        cursor.execute(SQL_COURSE_ROOM, val)
        message = SUCCEED_ALERT
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message}, safe=False)


SQL_BUILDING_LIST = '''select * from building where campusid = %(campusid)s '''
@api_view(['GET'])
def getBuildingList(request):
    params, invalid = collect_ints(request.query_params, 'campusid')
    if invalid:
        return invalid_params_response(invalid)
    val = {'campusid': params['campusid']}
    cursor = connection.cursor()
    message = ''
    buildings = {}
    try:
        cursor.execute(SQL_BUILDING_LIST, val)
        message = SUCCEED_ALERT
        buildings = cursor.fetchall()
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message, 'buildings': buildings}, safe=False)

SQL_ROOM_LIST = '''select * from room where campusid = %(campusid)s and building_id = %(building_id)s '''
@api_view(['GET'])
def getRoomList(request):
    params, invalid = collect_ints(request.query_params, 'campusid', 'building_id')
    if invalid:
        return invalid_params_response(invalid)
    val = {'campusid': params['campusid'], 'building_id': params['building_id']}
    cursor = connection.cursor()
    message = ''
    rooms = {}
    try:
        cursor.execute(SQL_ROOM_LIST, val)
        message = SUCCEED_ALERT
        rooms = cursor.fetchall()
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message, 'rooms': rooms}, safe=False)

SQL_STUDENT_INFO = '''select * from student where nuid = %(nuid)s '''
SQL_TA_INSERT = '''insert into ta values (%(nuid)s, %(name)s, %(email)s, %(campusid)s, %(collegeid)s,
%(department_id)s, %(phone)s, %(advisor)s, %(photo)s, %(grade)s, %(semester_hour)s, %(course_id)s) '''
@api_view(['GET'])
def addTaForCourse(request):
    params, invalid = collect_ints(request.query_params, 'ta_nuid', 'course_id')
    if invalid:
        return invalid_params_response(invalid)
    nuid = params['ta_nuid']
    course_id = params['course_id']
    cursor = connection.cursor()
    message = ''
    try:
        cursor.execute(SQL_STUDENT_INFO, {'nuid': nuid})
        student_info = cursor.fetchall()
    except Exception as e:
        print(e)
        cursor.close()
        return JsonResponse({'message': ERROR_ALERT}, safe=False)

    if not student_info:
        cursor.close()
        return JsonResponse({'message': NO_PERMISSION_ALERT}, safe=False)

    val = {
        'nuid': nuid,
        'name': student_info[0][1],
        'email': student_info[0][2],
        'campusid': student_info[0][4],
        'collegeid': student_info[0][5],
        'department_id': student_info[0][6],
        'phone': student_info[0][7],
        'advisor': student_info[0][8],
        'photo': student_info[0][9],
        'grade': student_info[0][10],
        'semester_hour': student_info[0][11],
        'course_id': course_id
    }

    try:
        cursor.execute(SQL_TA_INSERT, val)
        counts = cursor.rowcount
        if counts > 0:
            message = SUCCEED_ALERT
        else :
            message = ERROR_ALERT
    except  Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message}, safe=False)

SQL_TA_REMOVE = ''' delete from ta where nuid = %(nuid)s and course_id = %(course_id)s '''
@api_view(['GET'])
def removeTaForCourse(request):
    params, invalid = collect_ints(request.query_params, 'ta_nuid', 'course_id')
    if invalid:
        return invalid_params_response(invalid)
    val = {'nuid': params['ta_nuid'], 'course_id': params['course_id']}
    cursor = connection.cursor()
    message = ''

    try:
        cursor.execute(SQL_TA_REMOVE, val)
        counts = cursor.rowcount
        if counts > 0:
            message = SUCCEED_ALERT
        else :
            message = ERROR_ALERT
    except  Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message}, safe=False)
