# drop table room;
# drop table building;
# drop table registration;
# drop table ta;
# drop table course;
# drop table instructor;
# drop table student;
# drop table campus;
# drop table admin;
# drop table college;
# drop table advisor;
# drop table department;


create table department(department_id int primary key, department_name varchar(20), office_address varchar(100),
                        dean_name varchar(20), phone int, average_gpa double);

create table campus (campusid int primary key, campus_name varchar(45), location varchar(45));

create table building (building_id int primary key, building_name varchar(45), building_address varchar(45), campusid int,
                       num_of_classrooms int, foreign key (campusid) references campus(campusid));

create table instructor(employee_id int primary key, email varchar(100), phone int, name varchar(20), department_id int,
                        campusid int, office_hour time, foreign key (department_id) references department(department_id),
                        foreign key (campusid) references campus(campusid));

create table course(course_id int primary key, course_name varchar(255), instructor_id int, meeting_time time, max_num_of_students int, semester int,
                    semester_hrs int, registered_num_of_stud int, foreign key (instructor_id) references instructor(employee_id));


create table college(collegeid int primary key, name varchar(45));


create table advisor(employee_id int primary key, name varchar(45), email varchar(100), phone int, department_id int,
                     foreign key (department_id) references department(department_id), password varchar(20));

create table admin(employee_id int primary key, name varchar(45), email varchar(100), phone int, department_id int, foreign key (department_id)
    references department(department_id), password varchar(20));

create table ta(nuid int, name varchar(45), email varchar(100), campusid int, collegeid int, department_id int,
                phone int, advisor int(10), photo varchar(45), grade varchar(45), semester_hour varchar(45), course_id int,
                primary key (nuid, course_id),
                foreign key (advisor) references advisor(employee_id),
                foreign key (campusid) references campus(campusid), foreign key (collegeid) references college(collegeid),
                foreign key (department_id) references department(department_id));

create table room (room_id int primary key, building_id int, campusid int, max_capacity int, foreign key (building_id)
    references building(building_id), foreign key (campusid) references campus(campusid));

Create table student(nuid int primary key, name varchar(50), email varchar(100), bdate date, campusid int, collegeid int(10),
                     department_id int, phone int(11), advisor int(10), photo varchar(45), grade double, semesterhour int, password varchar(20),
                     foreign key (advisor) references advisor(employee_id),
                     foreign key (campusid) references campus(campusid),
                      foreign key (collegeid) references college(collegeid),
                      foreign key (department_id) references department(department_id));

create table registration(nuid int, course_id int, advisor_id int, grade double, status varchar(10),
                          foreign key (course_id) references course(course_id),
                          foreign key (advisor_id) references advisor(employee_id),
                          foreign key (nuid) references student(nuid),
                          primary key (nuid, course_id, advisor_id)
);
-- view 1 dpt1stu
-- see all department 1's students info
# drop view dpt1stu;
create view dpt1stu
    as select *
    from student
    where department_id = 1;
select * from dpt1stu;


-- view 2 dpt1ad
-- see all department 1's advisors' info
# drop view dpt1ad;
create view dpt1ad
    as select *
    from advisor
    where department_id = 1;
select * from dpt1ad;

-- procedure 1 update_capacity_for_course
-- Allow more student n to join a course
delimiter //
# DROP PROCEDURE update_capacity_for_course $$
create procedure update_capacity_for_course (IN param_course_id int, IN param_new_capacity int)
begin
    update course
    set max_num_of_students = param_new_capacity
    where course_id = param_course_id;
end //
delimiter ;
-- test
# select * from course where course_id = 5200;
# call update_capacity_for_course(5200, 50);
# select * from course where course_id = 5200;


-- procedure 2 cal_average_gpa_department
-- Calculate the average_gpa for given department id
delimiter  //
# DROP PROCEDURE cal_average_gpa_department $$
create procedure cal_average_gpa_department (IN param_department_id int)
begin
    update department
    set average_gpa = (select avg(grade) from student group by student.department_id having student.department_id = param_department_id)
    where department_id = param_department_id;
end //
delimiter ;

-- procedure 3 update_stu_semesterhour
-- Update student's semesterhour
delimiter  //
# DROP PROCEDURE update_stu_semesterhour $$
create procedure update_stu_semesterhour (IN param_student_id int, IN param_new_semesterhour int)
begin
    update student
    set semesterhour = param_new_semesterhour
    where nuid = param_student_id;
end //
delimiter ;
# select * from student where nuid = 1;
# call update_stu_semesterhour(1, 12);
# select * from student where nuid = 1;

-- trigger 1 student_violation
-- check if the bdate is larger than current time when a new tuple is inserted into student table
delimiter  //
# drop trigger student_violation $$
create trigger student_violation
    before insert
    on student
    for each row
begin
    if new.bdate > curdate() then
        set new.bdate = curdate();
    end if;
    if new.grade > 4 then
        set new.grade = 4;
    end if;
    if new.grade < 0 then
        set new.grade = 0;
    end if;
end //
delimiter ;
-- insert a new student with invalid bdate to test the trigger
# insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
#     (6, 'Bell', 'jone@northeastern.edu', '2200-02-21', 2, 12, 2, 100000001, 101, '/imgs/husky.png', 4.5, 16);
# select * from student;

-- trigger 2 cal_average_gpa_department_trigger
-- calculate the average_gpa for campus and department when a change in student table
delimiter  //
# drop trigger cal_average_gpa_department_trigger_insert $$
create trigger cal_average_gpa_department_trigger_insert
    after insert on student
    for each row
begin
    call cal_average_gpa_department(new.department_id);
end //
delimiter ;
-- test
# select * from department where department_id = 1;
# insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
#     (7, 'Apple', 'jone@northeastern.edu', '2200-02-21', 2, 12, 1, 100000001, 101, '/imgs/husky.png', 4, 16);
# select * from department where department_id = 1;


-- trigger 3 cal_average_gpa_department_trigger_update
-- calculate the average_gpa for campus and department when a change in student table
delimiter  //
# drop trigger cal_average_gpa_department_trigger_update $$
create trigger cal_average_gpa_department_trigger_update
    after update on student
    for each row
begin
    call cal_average_gpa_department(new.department_id);
end //
delimiter ;
-- test
# select * from department where department_id = 1;
# update student set grade = 3 where nuid = 1;
# select * from department where department_id = 1;

-- trigger 4 cal_average_gpa_department_trigger_delete
-- calculate the average_gpa for campus and department when a change in student table
delimiter  //
# drop trigger cal_average_gpa_department_trigger_delete $$
create trigger cal_average_gpa_department_trigger_delete
    after delete on student
    for each row
    begin
        call cal_average_gpa_department(old.department_id);
    end //
delimiter ;
# -- test
# select * from department where department_id = 1;
# delete from student where nuid = 7;
# select * from department where department_id = 1;



delimiter  //
create trigger gpa_status
    before update
    on registration
    for each row
begin
    if new.grade is not null and new.grade >= 3.0 then
        set new.status = 'completed';
    end if;
    if new.grade < 3.0 then
        set new.status = 'failed';
    end if;
end //
delimiter ;
