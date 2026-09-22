from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from django.db import connection

from .validators import (api_bad_request_guard, first_row, get_float,
                         get_int, get_str, to_int)
NO_PERMISSION_ALERT = "No records.\n Or No permission. This is not your student!"
SUCCEED_ALERT = "Succeed"
ERROR_ALERT = "Something wrong! Please try again!"
NOT_FOUND_ALERT = "No matching record found!"
SQL_COURSE_ADD_NUM = '''update course set registered_num_of_stud = registered_num_of_stud + 1 where course_id = %(course_id)s '''
SQL_COURSE_INFO = '''select * from course where course_id = %(course_id)s '''
SQL_REGISTRATION_APPROVAL = '''update registration set status = 'approved'
where nuid = %(nuid)s and status = 'pending' and advisor_id = %(advisor_id)s '''
SQL_REGISTRATION_PENDING_LIST = '''select * from registration where nuid = %(nuid)s and status = 'pending' and advisor_id = %(advisor_id)s'''
@api_view(['GET'])
@api_bad_request_guard
def approvePendingRequest(request):
    nuid = get_int(request.query_params, 'nuid')
    advisor_id = get_int(request.query_params, 'advisor_id')
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
@api_bad_request_guard
def rejectPendingRequest(request):
    val = {
        'nuid': get_int(request.query_params, 'nuid'),
        'advisor_id': get_int(request.query_params, 'advisor_id'),
    }
    cursor= connection.cursor()
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
@api_bad_request_guard
def removeOneApprovedCourse(request):
    val = {
        'nuid': get_int(request.query_params, 'nuid'),
        'course_id': get_int(request.query_params, 'course_id'),
        'advisor_id': get_int(request.query_params, 'advisor_id'),
    }
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
@api_bad_request_guard
def addOneApprovedCourse(request):
    nuid = get_int(request.query_params, 'nuid')
    course_id = get_int(request.query_params, 'course_id')
    advisor_id = get_int(request.query_params, 'advisor_id')
    message = addApprovedCourse(nuid, course_id, advisor_id)
    return JsonResponse({'message': message}, safe=False)

def addApprovedCourse(nuid, course_id, advisor_id):
    print('addApprovedCourse')
    nuid = to_int(nuid, 'nuid')
    course_id = to_int(course_id, 'course_id')
    advisor_id = to_int(advisor_id, 'advisor_id')
    cursor= connection.cursor()
    val = {'nuid': nuid, 'course_id': course_id, 'advisor_id': advisor_id}
    message = str(course_id) + " added successfully"
    try:
        cursor.execute('''SElect * from student where nuid = %(nuid)s ''', {'nuid': nuid})
        student_info = cursor.fetchall()
        student_row = first_row(student_info)
        if student_row is None or student_row[8] is None:
            return NO_PERMISSION_ALERT
        stu_advisor = to_int(student_row[8], 'advisor')
        print(stu_advisor)
        if stu_advisor != advisor_id:
            return NO_PERMISSION_ALERT
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
                    max_num_of_stus = to_int(c_info[0][4], 'max_num_of_students')
                    reg_num_of_stus = to_int(c_info[0][7], 'registered_num_of_stud')
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
    finally:
        cursor.close()
    print(message)
    return message


SQL_REGISTRATION_UPDATE_GPA = '''update registration set grade = %(grade)s where nuid= %(nuid)s and course_id = %(course_id)s and advisor_id = %(advisor_id)s '''
SQL_STUDENT_GPA_UPDATE = '''update student set grade = %(grade)s where nuid = %(nuid)s '''
SQL_STUDENT_GPA_CAL = '''SELECT avg(grade) from registration where grade is not null
group by nuid having nuid = %(nuid)s'''
@api_view(['GET'])
@api_bad_request_guard
def updateGPA(request):
    nuid = get_int(request.query_params, 'nuid')
    val = {
        'nuid': nuid,
        'course_id': get_int(request.query_params, 'course_id'),
        'advisor_id': get_int(request.query_params, 'advisor_id'),
        'grade': get_float(request.query_params, 'grade'),
    }
    cursor= connection.cursor()
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
            curr_gpa = gpas[0][0]
            val = {'grade': float(curr_gpa), 'nuid' : nuid}
            cursor.execute(SQL_STUDENT_GPA_UPDATE, val)
    except Exception as e:
        print(e)
        message = ERROR_ALERT
    cursor.close()
    return JsonResponse({'message': message}, safe=False)


SQL_STUDENT_INSERT = ''' insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, semesterhour, password) values (%(nuid)s, %(name)s, %(email)s,  %(bdate)s, %(campus)s, %(college)s, %(department)s, %(phone)s, %(advisor)s, 8, %(password)s) '''
SQL_NUID_CHECK = '''select * from student where nuid = %(nuid)s '''
@api_view(['GET'])
@api_bad_request_guard
def insertStudent(request):
    nuid = get_int(request.query_params, 'nuid')
    cursor= connection.cursor()
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
        'name': get_str(request.query_params, 'name', max_length=50),
        'email': get_str(request.query_params, 'email', max_length=100),
        'bdate': get_str(request.query_params, 'bdate', required=False, max_length=32),
        'campus': get_int(request.query_params, 'campus', required=False),
        'college': get_int(request.query_params, 'college', required=False),
        'department': get_int(request.query_params, 'department', required=False),
        'phone': get_str(request.query_params, 'phone', required=False, max_length=15),
        'advisor': get_int(request.query_params, 'advisor_id', required=False),
        'password': get_str(request.query_params, 'password', max_length=20),
    }
    message = SUCCEED_ALERT
    succeed = 0
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
@api_bad_request_guard
def updateHours(request):
    val = {
        'nuid': get_int(request.query_params, 'nuid'),
        'hours': get_int(request.query_params, 'hours', min_value=0),
    }
    cursor= connection.cursor()
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
@api_bad_request_guard
def updatePhone(request):
    val = {
        'advisor_id': get_int(request.query_params, 'advisor_id'),
        'phone': get_int(request.query_params, 'phone'),
    }
    cursor= connection.cursor()
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
@api_bad_request_guard
def saveClassRoom(request):
    val = {
        'course_id': get_int(request.query_params, 'course_id'),
        'campusid': get_int(request.query_params, 'campusid'),
        'building_id': get_int(request.query_params, 'building_id'),
        'room_id': get_int(request.query_params, 'room_id'),
    }
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
@api_bad_request_guard
def getBuildingList(request):
    val = {'campusid': get_int(request.query_params, 'campusid')}
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
@api_bad_request_guard
def getRoomList(request):
    val = {
        'campusid': get_int(request.query_params, 'campusid'),
        'building_id': get_int(request.query_params, 'building_id'),
    }
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
@api_bad_request_guard
def addTaForCourse(request):
    nuid = get_int(request.query_params, 'ta_nuid')
    course_id = get_int(request.query_params, 'course_id')
    cursor = connection.cursor()
    message = ''
    try:
        try:
            cursor.execute(SQL_STUDENT_INFO, {'nuid': nuid})
            student_row = first_row(cursor.fetchall())
        except Exception as e:
            print(e)
            return JsonResponse({'message': ERROR_ALERT}, safe=False)

        if student_row is None:
            return JsonResponse({'message': NOT_FOUND_ALERT}, status=404, safe=False)

        val = {
            'nuid': nuid,
            'name': student_row[1],
            'email': student_row[2],
            'campusid': student_row[4],
            'collegeid': student_row[5],
            'department_id': student_row[6],
            'phone': student_row[7],
            'advisor': student_row[8],
            'photo': student_row[9],
            'grade': student_row[10],
            'semester_hour': student_row[11],
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
    finally:
        cursor.close()
    return JsonResponse({'message': message}, safe=False)

SQL_TA_REMOVE = ''' delete from ta where nuid = %(nuid)s and course_id = %(course_id)s '''
@api_view(['GET'])
@api_bad_request_guard
def removeTaForCourse(request):
    val = {
        'nuid': get_int(request.query_params, 'ta_nuid'),
        'course_id': get_int(request.query_params, 'course_id'),
    }
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
