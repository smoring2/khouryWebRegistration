drop table admin;
drop table student;
drop table ta;
drop table registration;
drop table room;
drop table building;
drop table campus;
drop table course;
drop table instructor;
drop table college;
drop table advisor;
drop table department;

create table department(department_id int primary key, department_name varchar(20), office_address varchar(20),
                        dean_name varchar(20), phone int, average_gpa double);
insert into department(department_id, department_name, office_address, dean_name, phone, average_gpa) values (
                                                                                                    1, 'Computer Science', '4 N 2nd Street', 'Ed', 12345678, 3.88);
insert into department(department_id, department_name, office_address, dean_name, phone, average_gpa) values (
                                                                                                    2, 'Informatics', '4 N 2nd Street', 'James', 11111111, 3.44);

create table campus (campusid int primary key, campus_name varchar(45), location varchar(45));
insert into campus(campusid, campus_name, location) values (1, 'Silicon Valley', 'San Jose');
insert into campus(campusid, campus_name, location) values (2, 'Seattle', 'Seattle');


create table building (building_id int primary key, building_name varchar(45), building_address varchar(45), campusid int,
                       num_of_classrooms int, foreign key (campusid) references campus(campusid));

create table instructor(employee_id int primary key, email varchar(20), phone int, name varchar(20), department_id int,
                        campusid int, office_hour time, foreign key (department_id) references department(department_id),
                        foreign key (campusid) references campus(campusid));
insert into instructor(employee_id, email, phone, name, department_id, campusid, office_hour) values (
                                                                                                          1, 'lee@northeastern.edu', 11112222, 'Lee', 1, 1, '08:00:00');

create table course(course_id int primary key, instructor_id int, meeting_time time, max_num_of_students int, semester int,
                    semester_hrs int, registered_num_of_stud int, foreign key (instructor_id) references instructor(employee_id));
insert into course (course_id, instructor_id, meeting_time, max_num_of_students, semester, semester_hrs, registered_num_of_stud)
values (5200, 1, '18:00:00', 45, 2, 4, 37);
insert into course (course_id, instructor_id, meeting_time, max_num_of_students, semester, semester_hrs, registered_num_of_stud)
values (5520, 1, '10:00:00', 45, 2, 4, 40);

create table college(collegeid int primary key, name varchar(45));
insert into college(collegeid, name) values (12, 'Liberal art and sciences');
insert into college(collegeid, name) values (13, 'Engineering');

create table advisor(employee_id int primary key, name varchar(45), email varchar(45), phone int, department_id int,
                     foreign key (department_id) references department(department_id));
insert into advisor (employee_id, name, email, phone, department_id)
values (1, 'Chung Xiong', 'c.xiong@northeaster.edu', 1111111111, 1);
insert into advisor (employee_id, name, email, phone, department_id)
values (2, 'Anna Olson', 'a.olson@northeastern.edu', 222222222, 1);

create table admin(employee_id int primary key, name varchar(45), email varchar(45), phone int, department_id int, foreign key (department_id)
    references department(department_id));
insert into admin (employee_id, name, email, phone, department_id)
values (2, 'Anna Olson', 'a.olson@northeastern.edu', 222222222, 1);

create table ta(nuid int primary key, name varchar(45), email varchar(45), campusid int, collegeid int, department_id int,
                phone int, advisor varchar(45), photo varchar(45), grade varchar(45), semester_hour varchar(45), course_id int,
                foreign key (campusid) references campus(campusid), foreign key (collegeid) references college(collegeid),
                foreign key (department_id) references department(department_id));


/* Type of in_progress need to be determined. */
create table registration(nuid int primary key, course_id int, advisor_id int, approved bool, completed bool, failed bool,
                          in_progress bool, todo varchar(45), foreign key (course_id) references course(course_id));

create table room (room_id int primary key, building_id int, campusid int, max_capacity int, foreign key (building_id)
    references building(building_id), foreign key (campusid) references campus(campusid));

Create table student(nuid int primary key, name varchar(8), email varchar(45), bdate date, campusid int, collegeid int(10),
                     department_id int, phone int(11), advisor int(10), photo varchar(45), grade double, semesterhour int, foreign key
                         (campusid) references campus(campusid), foreign key (collegeid) references college(collegeid), foreign key
                         (department_id) references department(department_id));
insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
    (1, 'Husky', 'husky@northeastern.edu', '2022-10-17', 1, 12, 1, 111111111, 100, '/imgs/husky.png', 4.00, 4);
insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
    (2, 'James', 'james@northeastern.edu', '2000-11-06', 1, 13, 1, 100000000, 100, '/imgs/husky.png', 3.75, 20);
insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
    (3, 'Jone', 'jone@northeastern.edu', '2001-08-01', 2, 13, 2, 100000000, 101, '/imgs/husky.png', 3.21, 18);
insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
    (4, 'Johnson', 'jone@northeastern.edu', '1999-08-13', 2, 12, 2, 100000000, 101, '/imgs/husky.png', 3.46, 8);
insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
    (5, 'Edward', 'jone@northeastern.edu', '1998-02-21', 2, 12, 2, 100000000, 101, '/imgs/husky.png', 3.66, 16);


-- view 1 dpt1stu
-- see all department 1's students info
drop view dpt1stu;
create view dpt1stu
    as select *
    from student
    where department_id = 1;
select * from dpt1stu;


-- view 2 dpt1ad
-- see all department 1's advisors' info
drop view dpt1ad;
create view dpt1ad
    as select *
    from advisor
    where department_id = 1;
select * from dpt1ad;

-- procedure 1 update_capacity_for_course
-- Allow more student n to join a course
delimiter $$ ;
DROP PROCEDURE update_capacity_for_course $$
create procedure update_capacity_for_course (IN param_course_id int, IN param_new_capacity int)
begin
    update course
    set max_num_of_students = param_new_capacity
    where course_id = param_course_id;
end; $$
delimiter ; $$
-- test
select * from course where course_id = 5200;
call update_capacity_for_course(5200, 50);
select * from course where course_id = 5200;


-- procedure 2 cal_average_gpa_department
-- Calculate the average_gpa for given department id
delimiter $$ ;
DROP PROCEDURE cal_average_gpa_department $$
create procedure cal_average_gpa_department (IN param_department_id int)
begin
    update department
    set average_gpa = (select avg(grade) from student group by student.department_id having student.department_id = param_department_id)
    where department_id = param_department_id;
end; $$
delimiter ; $$

-- procedure 3 update_stu_semesterhour
-- Update student's semesterhour
delimiter $$ ;
DROP PROCEDURE update_stu_semesterhour $$
create procedure update_stu_semesterhour (IN param_student_id int, IN param_new_semesterhour int)
begin
    update student
    set semesterhour = param_new_semesterhour
    where nuid = param_student_id;
end; $$
delimiter ; $$
select * from student where nuid = 1;
call update_stu_semesterhour(1, 12);
select * from student where nuid = 1;

-- trigger 1 student_violation
-- check if the bdate is larger than current time when a new tuple is inserted into student table
delimiter $$ ;
drop trigger student_violation $$
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
end; $$
delimiter ; $$
-- insert a new student with invalid bdate to test the trigger
insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
    (6, 'Bell', 'jone@northeastern.edu', '2200-02-21', 2, 12, 2, 100000001, 101, '/imgs/husky.png', 4.5, 16);
select * from student;

-- trigger 2 cal_average_gpa_department_trigger
-- calculate the average_gpa for campus and department when a change in student table
delimiter $$ ;
drop trigger cal_average_gpa_department_trigger_insert $$
create trigger cal_average_gpa_department_trigger_insert
    after insert on student
    for each row
begin
    call cal_average_gpa_department(new.department_id);
end; $$
delimiter ; $$
-- test
select * from department where department_id = 1;
insert into student (nuid, name, email, bdate, campusid, collegeid, department_id, phone, advisor, photo, grade, semesterhour) values
    (7, 'Apple', 'jone@northeastern.edu', '2200-02-21', 2, 12, 1, 100000001, 101, '/imgs/husky.png', 4, 16);
select * from department where department_id = 1;


-- trigger 3 cal_average_gpa_department_trigger_update
-- calculate the average_gpa for campus and department when a change in student table
delimiter $$ ;
drop trigger cal_average_gpa_department_trigger_update $$
create trigger cal_average_gpa_department_trigger_update
    after update on student
    for each row
begin
    call cal_average_gpa_department(new.department_id);
end; $$
delimiter ; $$
-- test
select * from department where department_id = 1;
update student set grade = 3 where nuid = 1;
select * from department where department_id = 1;

-- trigger 3 cal_average_gpa_department_trigger_delete
-- calculate the average_gpa for campus and department when a change in student table
delimiter $$ ;
drop trigger cal_average_gpa_department_trigger_delete $$
create trigger cal_average_gpa_department_trigger_delete
    after delete on student
    for each row
    begin
        call cal_average_gpa_department(old.department_id);
    end; $$
delimiter ; $$
-- test
select * from department where department_id = 1;
delete from student where nuid = 7;
select * from department where department_id = 1;

