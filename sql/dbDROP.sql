-- CREATE DATABASE ph4;
-- USE ph4;

SHOW TRIGGERS;
drop trigger student_violation;
drop trigger cal_average_gpa_department_trigger_insert;
drop trigger cal_average_gpa_department_trigger_update;
drop trigger cal_average_gpa_department_trigger_delete;

drop table registration;
drop table admin;
drop table student;
drop table ta;
drop table course;
drop table instructor;
drop table room;
drop table building;
drop table campus;
drop table college;
drop table advisor;
drop table department;

drop view dpt1stu;
drop view dpt1ad;

DROP PROCEDURE update_capacity_for_course;
DROP PROCEDURE cal_average_gpa_department;
DROP PROCEDURE update_stu_semesterhour;

