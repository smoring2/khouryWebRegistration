from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from django.db import connection

SQL_REGISTRATION_APPROVAL = '''update registration set status = 'approved'
where nuid = %(nuid)s and status = 'pending' and advisor_id = %(advisor_id)s '''
@api_view(['GET'])
def approvePendingRequest(request):
    print("approvePendingRequest")
    nuid = request.query_params.get('nuid')
    advisor_id = request.query_params.get('advisor_id')
    cursor= connection.cursor()
    val = {'nuid': int(nuid), 'advisor_id': int(advisor_id)}
    message="succeed"
    try:
        cursor.execute(SQL_REGISTRATION_APPROVAL, val)
        counts = cursor.rowcount
        print(counts)
        if counts ==  0:
            message = "No permission\nThis is not your student! "
    except Exception as e:
        print(e)
        message = "No permission\nThis is not your student! "
    cursor.close()
    return JsonResponse({"message": message}, safe=False)

SQL_REGISTRATION_REJECTION = '''update registration set status = 'rejected'
where nuid= %(nuid)s and advisor_id = %(advisor_id)s and ( status = 'pending' or status ='approved') '''
@api_view(['GET'])
def rejectPendingRequest(request):
    nuid = request.query_params.get('nuid')
    advisor_id = request.query_params.get('advisor_id')
    cursor= connection.cursor()
    val = {'nuid': int(nuid), 'advisor_id': int(advisor_id)}
    message="succeed"
    try:
        cursor.execute(SQL_REGISTRATION_REJECTION, val)
    except:
       message = "No permssion\nThis is not your student! "
    cursor.close()
    return JsonResponse({"message": message}, safe=False)


SQL_REGISTRATION_REMOVE = '''update registration set status = 'rejected'
where nuid= %(nuid)s and course_id = %(course_id)s and advisor_id = %(advisor_id)s'''
@api_view(['GET'])
def removeOneApprovedCourse(request):
    nuid = request.query_params.get('nuid')
    course_id = request.query_params.get('course_id')
    advisor_id = request.query_params.get('advisor_id')
    val = {'nuid': int(nuid), 'course_id': int(course_id), 'advisor_id': int(advisor_id)}
    cursor= connection.cursor()
    message = "succeed"
    try:
        cursor.execute(SQL_REGISTRATION_REMOVE, val)
        counts = cursor.rowcount
        if counts == 0:
            message = "No permssion\nThis is not your student! "
    except:
        message = "No permssion\nThis is not your student! "
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
    nuid = request.query_params.get('nuid')
    course_id = request.query_params.get('course_id')
    advisor_id = request.query_params.get('advisor_id')
    cursor= connection.cursor()
    val = {'nuid': int(nuid), 'course_id': int(course_id), 'advisor_id': int(advisor_id)}
    message = "succeed"
    try:
        cursor.execute(SQL_REGISTRATION_INFO, val)
        registration_info = cursor.fetchall()
        if registration_info:
            registration_status = registration_info[0][4]
            if registration_status == 'pending'  or registration_status == 'rejected':
                 cursor.execute(SQL_REGISTRATION_ADD, val)
            else:
                message = "Student already has taken this course"
        else:
            cursor.execute(SQL_REGISTRATION_INSERT, val)
    except:
        message = "No permssion\nThis is not your student! "
    cursor.close()
    return JsonResponse({'message': message}, safe=False)

SQL_REGISTRATION_UPDATE_GPA = '''update registration set grade = %(grade)s where nuid= %(nuid)s and course_id = %(course_id)s and advisor_id = %(advisor_id)s '''
SQL_STUDENT_GPA_UPDATE = '''update student set grade = %(grade)s where nuid = %(nuid)s '''
SQL_STUDENT_GPA_CAL = '''SELECT avg(grade) from registration where grade is not null
group by nuid having nuid = %(nuid)s'''
@api_view(['GET'])
def updateGPA(request):
    nuid = request.query_params.get('nuid')
    course_id = request.query_params.get('course_id')
    advisor_id = request.query_params.get('advisor_id')
    grade = request.query_params.get('grade')
    cursor= connection.cursor()
    val = {'nuid': int(nuid), 'course_id': int(course_id), 'advisor_id': int(advisor_id), 'grade': float(grade)}
    message = "succeed"
    try:
        cursor.execute(SQL_REGISTRATION_UPDATE_GPA, val)
        print(cursor.fetchall())
        cursor.execute(SQL_STUDENT_GPA_CAL, val)
        gpas = cursor.fetchall()
        curr_gpa = gpas[0][0]
        val = {'grade': float(curr_gpa), 'nuid' : int(nuid)}
        cursor.execute(SQL_STUDENT_GPA_UPDATE, val)
        counts = cursor.rowcount
        print(counts)
        if counts ==  0:
            message = "No permission\nThis is not your student! "
    except Exception as e:
        print(e)
        message = "No permssion\nThis is not your student! "
    cursor.close()
    return JsonResponse({'message': message}, safe=False)


SQL_STUDENT_INSERT = ''' insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, semesterhour, password) values (%(nuid)s, %(name)s, %(email)s,  %(bdate)s, %(campus)s, %(college)s, %(department)s, %(phone)s, %(advisor)s, 8, %(password)s) '''
SQL_NUID_CHECK = '''select * from student where nuid = %(nuid)s '''
@api_view(['GET'])
def insertStudent(request):
    print(request.query_params)
    nuid = request.query_params.get('nuid')
    cursor= connection.cursor()
    val = {'nuid': int(nuid)}
    cursor.execute(SQL_NUID_CHECK, val)
    print("test-mysql")
    res = cursor.fetchall()
    if res:
        message = "This NUID has been taken. Please use choose different one"
        return JsonResponse({'message': message, "succeed": 0}, safe=False)

    name = request.query_params.get('name')
    email = request.query_params.get('email')
    bdate = request.query_params.get('bdate')
    campus = request.query_params.get('campus')
    college = request.query_params.get('college')
    department = request.query_params.get('department')
    phone = request.query_params.get('phone')
    advisor = request.query_params.get('advisor_id')
    password = request.query_params.get('password')
    val = {
        'nuid' : int(nuid),
        'name': name,
        'email': email,
        'bdate': bdate,
        'campus': campus,
        'college': college,
        'department': department,
        'phone': phone,
        'advisor':advisor,
        'password': password
    }
    print("test-val")
    print(val)
    message = "succeed"
    succeed = 0
    try:
        cursor.execute(SQL_STUDENT_INSERT, val)
        succeed = 1
    except Exception as e:
        print(e)
        message = "Something wrong. Please try again"
    cursor.close()
    return JsonResponse({'message': message, "succeed": succeed}, safe=False)

SQL_STUDENT_UPDATE_HOURS = '''update student set semesterhour= %(hours)s where nuid = %(nuid)s '''
@api_view(['GET'])
def updateHours(request):
    nuid = request.query_params.get('nuid')
    hours = request.query_params.get('hours')
    cursor= connection.cursor()
    val = {'nuid': int(nuid), 'hours': int(hours)}
    message = ''
    try:
        cursor.execute(SQL_STUDENT_UPDATE_HOURS, val)
        message = 'succeed!'
    except:
        message = 'something wrong! Please try again!'
    cursor.close()
    print(message)
    return JsonResponse({'message': message}, safe=False)


SQL_ADVISOR_UPDATE_PHONE = '''update advisor set phone = %(phone)s where employee_id = %(advisor_id)s '''
@api_view(['GET'])
def updatePhone(request):
    advisor_id = request.query_params.get("advisor_id")
    phone = request.query_params.get('phone')
    cursor= connection.cursor()
    val = {'advisor_id': int(advisor_id), 'phone': int(phone)}
    message = 'succeed'
    try:
        cursor.execute(SQL_ADVISOR_UPDATE_PHONE, val)
    except Exception as e:
        print(e)
        message = 'something wrong! Please try again!'
    cursor.close()
    return JsonResponse({'message': message}, safe=False)

SQL_COURSE_ROOM = '''update course set campusid = %(campusid)s,
building_id = %(building_id)s, room_id = %(room_id)s where course_id = %(course_id)s '''
@api_view(['GET'])
def saveClassRoom(request):
    course_id = request.query_params.get('course_id')
    campusid = request.query_params.get('campusid')
    building_id = request.query_params.get('building_id')
    room_id = request.query_params.get('room_id')
    val = {'course_id': int(course_id), 'campusid': int(campusid), 'building_id': int(building_id), 'room_id': int(room_id)}
    cursor = connection.cursor()
    succeed = "Succeed"
    failed = "Something wrong. Please try again!"
    message = ''
    try:
        cursor.execute(SQL_COURSE_ROOM, val)
        message = succeed
    except Exception as e:
        print(e)
        message = failed
    cursor.close()
    return JsonResponse({'message': message}, safe=False)


SQL_BUILDING_LIST = '''select * from building where campusid = %(campusid)s '''
@api_view(['GET'])
def getBuildingList(request):
    campusid = request.query_params.get('campusid')
    val = {'campusid': int(campusid)}
    cursor = connection.cursor()
    succeed = "Succeed"
    failed = "Something wrong. Please try again!"
    message = ''
    buildings = {}
    try:
        cursor.execute(SQL_BUILDING_LIST, val)
        message = succeed
        buildings = cursor.fetchall()
    except Exception as e:
        print(e)
        message = failed
    cursor.close()
    return JsonResponse({'message': message, 'buildings': buildings}, safe=False)

SQL_ROOM_LIST = '''select * from room where campusid = %(campusid)s and building_id = %(building_id)s '''
@api_view(['GET'])
def getRoomList(request):
    campusid = request.query_params.get('campusid')
    building_id = request.query_params.get('building_id')
    val = {'campusid': int(campusid), 'building_id': int(building_id)}
    cursor = connection.cursor()
    failed = "Something wrong. Please try again!"
    message = ''
    rooms = {}
    try:
        cursor.execute(SQL_ROOM_LIST, val)
        message = succeed
        rooms = cursor.fetchall()
    except Exception as e:
        print(e)
        message = failed
    cursor.close()
    return JsonResponse({'message': message, 'rooms': rooms}, safe=False)

SQL_STUDENT_INFO = '''select * from student where nuid = %(nuid)s '''
SQL_TA_INSERT = '''insert into ta values (%(nuid)s, %(name)s, %(email)s, %(campusid)s, %(collegeid)s,
%(department_id)s, %(phone)s, %(advisor)s, %(photo)s, %(grade)s, %(semester_hour)s, %(course_id)s) '''
@api_view(['GET'])
def addTaForCourse(request):
    nuid = request.query_params.get('ta_nuid')
    course_id = request.query_params.get('course_id')
    val = {'nuid': int(nuid)}
    cursor = connection.cursor()
    cursor.execute(SQL_STUDENT_INFO, val)
    student_info = cursor.fetchall()
    val = {
        'nuid': int(nuid),
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
        'course_id': int(course_id)
    }
    message = ''
    succeed = 'succeed'
    failed = 'Something wrong. Please try again!'
    try:
        cursor.execute(SQL_TA_INSERT, val)
        counts = cursor.rowcount
        if counts > 0:
            message = succeed
        else :
            message = failed
    except  Exception as e:
        print(e)
        message = failed
    return JsonResponse({'message': message}, safe=False)

