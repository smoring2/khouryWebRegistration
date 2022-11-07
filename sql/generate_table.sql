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
dean_name varchar(20), phone int);
insert into department(department_id, department_name, office_address, dean_name, phone) values (
1, 'Computer Science', '4 N 2nd Street', 'Ed', 12345678);
insert into department(department_id, department_name, office_address, dean_name, phone) values (
2, 'Informatics', '4 N 2nd Street', 'James', 11111111);

create table campus (campus_id int primary key, campus_name varchar(45), location varchar(45));
insert into campus(campus_id, campus_name, location) values (1, 'Silicon Valley', 'San Jose');
insert into campus(campus_id, campus_name, location) values (2, 'Seattle', 'Seattle');


create table building (building_id int primary key, building_name varchar(45), building_address varchar(45), campus_id int,
num_of_classrooms int, foreign key (campus_id) references campus(campus_id));

create table instructor(employee_id int primary key, email varchar(20), phone int, name varchar(20), department_id int,
campus_id int, office_hour time, foreign key (department_id) references department(department_id),
foreign key (campus_id) references campus(campus_id));
insert into instructor(employee_id, email, phone, name, department_id, campus_id, office_hour) values (
1, 'lee@northeastern.edu', 11112222, 'Lee', 1, 1, '08:00:00');

create table course(course_id int primary key, instructor_id int, meeting_time time, max_num_of_students int, semester int,
semester_hrs int, registered_num_of_stud int, foreign key (instructor_id) references instructor(employee_id));
insert into course (course_id, instructor_id, meeting_time, max_num_of_students, semester, semester_hrs, registered_num_of_stud)
values (5200, 1, '18:00:00', 45, 2, 4, 37);
insert into course (course_id, instructor_id, meeting_time, max_num_of_students, semester, semester_hrs, registered_num_of_stud)
values (5520, 1, '10:00:00', 45, 2, 4, 40);

create table college(college_id int primary key, name varchar(45));
insert into college(college_id, name) values (12, 'Liberal art and sciences');
insert into college(college_id, name) values (13, 'Engineering');

create table advisor(employee_id int primary key, email varchar(45), phone int, department_id int, 
foreign key (department_id) references department(department_id));

create table admin(employee_id int primary key, email varchar(45), phone int, department_id int, foreign key (department_id)
references department(department_id));

create table ta(nuid int primary key, name varchar(45), email varchar(45), campus_id int, college_id int, department_id int,
phone int, advisor varchar(45), photo varchar(45), grade varchar(45), semester_hour varchar(45), course_id int,
foreign key (campus_id) references campus(campus_id), foreign key (college_id) references college(college_id),
foreign key (department_id) references department(department_id));


/* Type of in_progress need to be determined. */
create table registration(nuid int primary key, course_id int, advisor_id int, approved bool, completed bool, failed bool,
in_progress bool, todo varchar(45), foreign key (course_id) references course(course_id));

create table room (room_id int primary key, building_id int, campus_id int, max_capacity int, foreign key (building_id)
references building(building_id), foreign key (campus_id) references campus(campus_id));

Create table student(nuid int primary key, name varchar(8), email varchar(45), bdate date, campus_id int, college_id int(10),
department_id int, phone int(11), advisor int(10), photo varchar(45), grade double, semesterhour int, foreign key
(campus_id) references campus(campus_id), foreign key (college_id) references college(college_id), foreign key 
(department_id) references department(department_id));
insert into student (nuid, name, email, bdate, campus_id, college_id, department_id, phone, advisor, photo, grade, semesterhour) values 
(1, 'Husky', 'husky@northeastern.edu', '2022-10-17', 1, 12, 1, 111111111, 100, '/imgs/husky.png', 4.00, 4);
insert into student (nuid, name, email, bdate, campus_id, college_id, department_id, phone, advisor, photo, grade, semesterhour) values 
(2, 'James', 'james@northeastern.edu', '2000-11-06', 1, 13, 1, 100000000, 100, '/imgs/husky.png', 3.75, 20);
insert into student (nuid, name, email, bdate, campus_id, college_id, department_id, phone, advisor, photo, grade, semesterhour) values 
(3, 'Jone', 'jone@northeastern.edu', '2001-08-01', 2, 13, 2, 100000000, 101, '/imgs/husky.png', 3.21, 18);
insert into student (nuid, name, email, bdate, campus_id, college_id, department_id, phone, advisor, photo, grade, semesterhour) values 
(4, 'Johnson', 'jone@northeastern.edu', '1999-08-13', 2, 12, 2, 100000000, 101, '/imgs/husky.png', 3.46, 8);
insert into student (nuid, name, email, bdate, campus_id, college_id, department_id, phone, advisor, photo, grade, semesterhour) values 
(5, 'Edward', 'jone@northeastern.edu', '1998-02-21', 2, 12, 2, 100000000, 101, '/imgs/husky.png', 3.66, 16);
