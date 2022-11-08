-- SQL 1: Select the student id and student name with the highest GPA in the given department.
select d.department_name, s.nuid, s.name, s.grade as 'dept_highest_gpa'
from student s
inner join department d
on s.department_id = d.department_Id
where s.department_id = '1'
order by grade
limit 1;

-- SQL 2: Given the student's name, get which department the student belongs to.
select d.department_name
from department d
inner join student s
on s.department_id = d.department_id
where s.name = 'Lily';

-- SQL 3: Select max GPA from each department.
select department_name, grade
from department d,
	(select department_id, max(grade) as grade
	from student
	group by department_id
) c
where d.department_id = c.department_id;

-- SQL 4: Given the selected term, return all courses with the course number, instructor name, campus, meeting time,
-- and course capacity.
select c.course_id, i.name, cam.campus_name, c.meeting_time, c.max_num_of_students as capacity
from course c
inner join instructor i
on c.instructor_id = i.employee_id
inner join campus cam
on cam.campusid = i.campusid
where c.semester = 2;


-- SQL 5: Given the student ID, return all courses that the student have completed.
select s.name, r.course_id as course_completed
from student s
inner join registration r
on s.nuid = r.nuid
and r.completed = true
and s.nuid = 1;