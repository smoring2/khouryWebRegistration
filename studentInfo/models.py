# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admin(models.Model):
    employee_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    department = models.ForeignKey('Department', models.DO_NOTHING, blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin'


class Advisor(models.Model):
    employee_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    department = models.ForeignKey('Department', models.DO_NOTHING, blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'advisor'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Building(models.Model):
    building_id = models.IntegerField(primary_key=True)
    building_name = models.CharField(max_length=45, blank=True, null=True)
    building_address = models.CharField(max_length=45, blank=True, null=True)
    campusid = models.ForeignKey('Campus', models.DO_NOTHING, db_column='campusid', blank=True, null=True)
    num_of_classrooms = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'building'


class Campus(models.Model):
    campusid = models.IntegerField(primary_key=True)
    campus_name = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'campus'


class College(models.Model):
    collegeid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'college'


class Course(models.Model):
    course_id = models.IntegerField(primary_key=True)
    course_name = models.CharField(blank=True, null=True, max_length=100)
    instructor = models.ForeignKey('Instructor', models.DO_NOTHING, blank=True, null=True)
    meeting_time = models.TimeField(blank=True, null=True)
    max_num_of_students = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    semester_hrs = models.IntegerField(blank=True, null=True)
    registered_num_of_stud = models.IntegerField(blank=True, null=True)
    department = models.ForeignKey('Department', models.DO_NOTHING, blank=True, null=True)
    campusid = models.ForeignKey(Campus, models.DO_NOTHING, db_column='campusid', blank=True, null=True)
    building = models.ForeignKey(Building, models.DO_NOTHING, blank=True, null=True)
    room = models.ForeignKey('Room', models.DO_NOTHING, blank=True, null=True)
    date = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course'


class Department(models.Model):
    department_id = models.IntegerField(primary_key=True)
    department_name = models.CharField(max_length=20, blank=True, null=True)
    office_address = models.CharField(max_length=100, blank=True, null=True)
    dean_name = models.CharField(max_length=20, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    average_gpa = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'department'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Instructor(models.Model):
    employee_id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    campusid = models.ForeignKey(Campus, models.DO_NOTHING, db_column='campusid', blank=True, null=True)
    office_hour = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'instructor'


class Registration(models.Model):
    nuid = models.IntegerField(primary_key=True)
    course = models.ForeignKey(Course, models.DO_NOTHING)
    advisor_id = models.IntegerField()
    grade = models.DecimalField(max_digits=3, decimal_places=2)
    status = models.CharField(max_length=10)


    class Meta:
        managed = False
        db_table = 'registration'
        unique_together = (('nuid', 'course', 'advisor_id'),)


class Room(models.Model):
    room_id = models.IntegerField(primary_key=True)
    building = models.ForeignKey(Building, models.DO_NOTHING, blank=True, null=True)
    campusid = models.ForeignKey(Campus, models.DO_NOTHING, db_column='campusid', blank=True, null=True)
    max_capacity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'room'


class Student(models.Model):
    nuid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    bdate = models.DateField(blank=True, null=True)
    campusid = models.ForeignKey(Campus, models.DO_NOTHING, db_column='campusid', blank=True, null=True)
    collegeid = models.ForeignKey(College, models.DO_NOTHING, db_column='collegeid', blank=True, null=True)
    department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    advisor = models.ForeignKey(Advisor, models.DO_NOTHING, db_column='advisor', blank=True, null=True)
    photo = models.CharField(max_length=45, blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    semesterhour = models.IntegerField(blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student'


class Ta(models.Model):
    nuid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    campusid = models.ForeignKey(Campus, models.DO_NOTHING, db_column='campusid', blank=True, null=True)
    collegeid = models.ForeignKey(College, models.DO_NOTHING, db_column='collegeid', blank=True, null=True)
    department = models.ForeignKey(Department, models.DO_NOTHING, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    advisor = models.ForeignKey(Advisor, models.DO_NOTHING, db_column='advisor', blank=True, null=True)
    photo = models.CharField(max_length=45, blank=True, null=True)
    grade = models.CharField(max_length=45, blank=True, null=True)
    semester_hour = models.CharField(max_length=45, blank=True, null=True)
    course_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ta'
