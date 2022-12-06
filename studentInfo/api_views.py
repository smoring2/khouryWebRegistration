from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from django.db import connection
NO_PERMISSION_ALERT = "No permission\nThis is not your student!"
SUCCEED_ALERT = "Succeed"
ERROR_ALERT = "Something wrong! Please try again!"
SQL_COURSE_ADD_NUM = '''update course set registered_num_of_stud = registered_num_of_stud + 1 where course_id = %(course_id)s '''
SQL_COURSE_INFO = '''select * from course where course_id = %(course_id)s '''
SQL_REGISTRATION_APPROVAL = '''update registration set status = 'approved'
where nuid = %(nuid)s and status = 'pending' and advisor_id = %(advisor_id)s '''
SQL_REGISTRATION_PENDING_LIST = '''select * from registration where nuid = %(nuid)s and status = 'pending' and advisor_id = %(advisor_id)s'''
@api_view(['GET'])
def approvePendingRequest(request):
    nuid = request.query_params.get('nuid')
    advisor_id = request.query_params.get('advisor_id')
    val = {'nuid': int(nuid), 'advisor_id': int(advisor_id)}
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
@api_view(['GET'])
def rejectPendingRequest(request):
    nuid = request.query_params.get('nuid')
    advisor_id = request.query_params.get('advisor_id')
    cursor= connection.cursor()
    val = {'nuid': int(nuid), 'advisor_id': int(advisor_id)}
    message="succeed"
    try:
        cursor.execute(SQL_REGISTRATION_REJECTION, val)
        counts = cursor.rowcount
        if counts == 0:
            message = NO_PERMISSION_ALERT
    except:
       message = ERROR_ALERT
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
            message = NO_PERMISSION_ALERT
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
    nuid = request.query_params.get('nuid')
    course_id = request.query_params.get('course_id')
    advisor_id = request.query_params.get('advisor_id')
    message = addApprovedCourse(nuid, course_id, advisor_id)
    return JsonResponse({'message': message}, safe=False)

def addApprovedCourse(nuid, course_id, advisor_id):
    print('addApprovedCourse')
    cursor= connection.cursor()
    val = {'nuid': int(nuid), 'course_id': int(course_id), 'advisor_id': int(advisor_id)}
    print(val)
    message = str(course_id) + " added successfully"
    cursor.execute('''SElect * from student where nuid = %(nuid)s ''', {'nuid': int(nuid)})
    student_info = cursor.fetchall()
    if student_info:
        stu_advisor = int(student_info[0][8])
        print(stu_advisor)
        if stu_advisor == int(advisor_id):
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
                        max_num_of_stus = int(c_info[0][4])
                        reg_num_of_stus = int(c_info[0][7])
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
    cursor.close()
    return message


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
        counts = cursor.rowcount
        print(counts)
        if counts ==  0:
            message = NO_PERMISSION_ALERT
        else:
            cursor.execute(SQL_STUDENT_GPA_CAL, val)
            gpas = cursor.fetchall()
            curr_gpa = gpas[0][0]
            val = {'grade': float(curr_gpa), 'nuid' : int(nuid)}
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
def updateHours(request):
    nuid = request.query_params.get('nuid')
    hours = request.query_params.get('hours')
    cursor= connection.cursor()
    val = {'nuid': int(nuid), 'hours': int(hours)}
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
    advisor_id = request.query_params.get("advisor_id")
    phone = request.query_params.get('phone')
    cursor= connection.cursor()
    val = {'advisor_id': int(advisor_id), 'phone': int(phone)}
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
    course_id = request.query_params.get('course_id')
    campusid = request.query_params.get('campusid')
    building_id = request.query_params.get('building_id')
    room_id = request.query_params.get('room_id')
    val = {'course_id': int(course_id), 'campusid': int(campusid), 'building_id': int(building_id), 'room_id': int(room_id)}
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
    campusid = request.query_params.get('campusid')
    val = {'campusid': int(campusid)}
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
    campusid = request.query_params.get('campusid')
    building_id = request.query_params.get('building_id')
    val = {'campusid': int(campusid), 'building_id': int(building_id)}
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
    return JsonResponse({'message': message}, safe=False)

SQL_TA_REMOVE = ''' delete from ta where nuid = %(nuid)s and course_id = %(course_id)s '''
@api_view(['GET'])
def removeTaForCourse(request):
    nuid = request.query_params.get('ta_nuid')
    course_id = request.query_params.get('course_id')
    val = {'nuid': int(nuid), 'course_id': int(course_id)}
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
        message = failed
    return JsonResponse({'message': message}, safe=False)

