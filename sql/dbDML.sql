insert into department values (1, 'Computer Science', '4 N 2nd Street, San Jose, CA', 'Ed', 12345678, 0),
       (2, 'Informatics', '4 N 2nd Street, San Jose, CA', 'James', 11111111, 0),
       (3, 'Data Science', '4 N 2nd Street, San Jose, CA', 'David', 22222222, 0),
       (4, 'Data Analytics', '4 N 2nd Street, San Jose, CA', 'Charles', 33333333, 0),
       (5, 'Information System', '4 N 2nd Street, San Jose, CA', 'Ross', 44444444, 0),
       (6, 'Quantitative Finance', '360 Huntington Ave, Boston, MA', 'Mike', 55555555, 0),
       (7, 'Softwere Engineering', '360 Huntington Ave, Boston, MA', 'Anna', 66666666, 0);

insert into campus values (1, 'Silicon Valley', 'San Jose'),
       (2, 'Seattle', 'Seattle'),
       (3, 'Boston', 'Boston'),
       (4, 'Charlotte', 'Charlotte'),
       (5, 'San Francisco', 'San Francisco'),
       (6, 'Portland', 'Portland'),
       (7, 'Vancouver', 'Vancouver');

insert into building values (1, 'Ell Hall', '140 The Fenway', 1, 20),
       (2, 'Fenway Center', '141 The Fenway', 2, 15),
       (3, 'Forsyth Building', '271 Huntington', 3, 20),
       (4, 'Egan Research Center', '236 Huntington', 4, 30),
       (5, 'Dockser Hall', '1216 Massachusetts Ave', 5, 10),
       (6, 'Cullinane Hall', '177 Huntington', 6, 20),
       (7, 'Cushing Hall', '780 Columbus Ave', 7, 20);

insert into room values (1, 1, 1, 80),
                        (2, 2, 2, 100),
                        (3, 3, 3, 90),
                        (4, 4, 4, 120),
                        (5, 5, 5, 100),
                        (6, 6, 6, 100),
                        (7, 7, 7, 80);


insert into instructor values (1, 'lee@northeastern.edu', 11112222, 'Lee', 1, 1, '08:00:00'),
       (2, 'don@northeastern.edu', 11110000, 'Don', 2, 2, '10:00:00'),
       (3, 'alex@northeastern.edu', 22220000, 'Alex', 3, 3, '11:00:00'),
       (4, 'peggy@northeastern.edu', 33330000, 'Peggy', 4, 4, '13:00:00'),
       (5, 'betty@northeastern.edu', 44440000, 'Betty', 5, 5, '14:00:00'),
       (6, 'peter@northeastern.edu', 55550000, 'Peter', 6, 6, '15:00:00'),
       (7, 'alicia@northeastern.edu', 66660000, 'Alicia', 7, 7, '16:00:00');

insert into course values (5200, 'Database Management Systems', 1, '18:00:00', 45, 2, 4, 37, 1, null, null, null),
       (5520, 'Mobile Application Development', 1, '10:00:00', 45, 2, 4, 40, 1, null, null, null),
       (6620, 'Fundamentals of Cloud Computing', 2, '10:00:00', 70, 1, 4, 50, 1, null, null, null),
       (5800, 'Algorithms', 3, '18:00:00', 45, 3, 4, 35, 1, null, null, null),
       (5008, 'Data Structures, Algorithms, and Their Applications within Computer Systems', 4, '14:00:00', 50, 1, 4,
        40, 1, null, null, null),
       (5004, 'Object-Oriented Design', 5, '13:00:00', 60, 1, 4, 50, 1, null, null, null),
       (6650, 'Building Scalable Distributed System', 6, '19:00:00', 40, 3, 4, 40, 1, null, null, null);

insert into college values (12, 'Liberal art and sciences'),
       (13, 'Engineering'),
       (14, 'College of Science'),
       (15, 'D’Amore-McKim School of Business'),
       (16, 'Bouvé College of Health Sciences'),
       (17, 'School of Law'),
       (18, 'College of Professional Studies');

insert into advisor values (8, 'Anna', 'anna@northeastern.edu', 77770000, 1, '123456778'),
       (9, 'Cary', 'cary@northeastern.edu', 88880000, 2, '123456778'),
       (10, 'Diane', 'diane@northeastern.edu', 99990000, 3, '123456778'),
       (11, 'Will', 'will@northeastern.edu', 11113333, 4, '123456778'),
       (12, 'Zach', 'zach@northeastern.edu', 22224444, 5, '123456778'),
       (13, 'Eli', 'eli@northeastern.edu', 33335555, 6, '123456778'),
       (14, 'Grace', 'grace@northeastern.edu', 44446666, 7, '123456778');

insert into admin values (15, 'kalinda', 'kalinda@northeastern.edu', 66668888, 1, '123456778'),
       (16, 'claire', 'claire@northeastern.edu', 12340000, 2, '123456778'),
       (17, 'phil', 'phil@northeastern.edu', 12341000, 3, '123456778'),
       (18, 'sarah', 'sarah@northeastern.edu', 12342000, 4, '123456778'),
       (19, 'jay', 'jay@northeastern.edu', 12343000, 5, '123456778'),
       (20, 'luke', 'luke@northeastern.edu', 12344000, 6, '123456778'),
       (21, 'cam', 'cam@northeastern.edu', 12345000, 6, '123456778');

insert into ta values (1, 'Lily', 'lily@northeastern.edu', 1, 12, 1, 43211000, 8, '/imgs/lily.png', 6, 4, 5200),
       (2, 'Gloria', 'gloria@northeastern.edu', 1, 12, 1, 43212000, 8, '/imgs/gloria.png', 6, 4, 5520),
       (10, 'Manny', 'manny@northeastern.edu', 2, 13, 2, 43213000, 9, '/imgs/manny.png', 5, 4, 6620),
       (3, 'Mitchelle', 'mitchelle@northeastern.edu', 2, 13, 2, 43214000, 9, '/imgs/mitch.png', 7, 4, 5520),
       (5, 'Joe', 'joe@northeastern.edu', 4, 15, 4, 43215000, 10, '/imgs/joe.png', 6, 4, 6620),
       (8, 'Dede', 'dede@northeastern.edu', 5, 16, 5, 43216000, 11, '/imgs/dede.png', 6, 4, 5004),
       (9, 'Pepper', 'pepper@northeastern.edu', 6, 17, 6, 43217000, 11, '/imgs/peper.png', 6, 4, 5004);

insert into student values (1, 'Lily', 'lily@northeastern.edu', '2000-10-17', 1, 12, 1, 43211000, 8, '/imgs/lily.png', 4.00, 4, '123456778'),
    (2, 'Gloria', 'gloria@northeastern.edu', '2000-11-06', 1, 12, 1, 43212000, 8, '/imgs/gloria.png', 3.75, 20,
     '123456778'),
    (3, 'Mitchelle', 'mitchelle@northeastern.edu', '2001-08-01', 2, 13, 2, 43214000, 9, '/imgs/mitchelle.png', 3.21, 18,
     '123456778'),
    (4, 'Johnson', 'johnson@northeastern.edu', '1999-08-13', 2, 13, 2, 100000000, 9, '/imgs/johnson.png', 3.46, 8,
     '123456778'),
    (5, 'Joe', 'joe@northeastern.edu', '1998-02-21', 2, 13, 2, 43215000, 9, '/imgs/joe.png', 3.66, 16, '123456778'),
    (6, 'Lana', 'lana@northeastern.edu', '1998-02-21', 3, 14, 3, 43215000, 10, '/imgs/lana.png', 4.00, 12, '123456778'),
    (7, 'Kurt', 'kurt@northeastern.edu', '1998-02-21', 4, 15, 4, 43215000, 11, '/imgs/kurt.png', 3.50, 10, '123456778'),
    (8, 'Dede', 'dede@northeastern.edu', '1998-02-21', 5, 16, 5, 43215000, 12, '/imgs/dede.png', 2.80, 16, '123456778'),
    (9, 'Pepper', 'pepper@northeastern.edu', '1998-02-21', 6, 17, 6, 43215000, 13, '/imgs/pepper.png', 2.30, 20,
     '123456778'),
    (10, 'Manny', 'manny@northeastern.edu', '1998-02-21', 7, 18, 7, 43215000, 14, '/imgs/manny.png', 3.60, 10,
     '123456778');

insert into registration values (1, 6620, 8, null, 'pending'),
                                (2, 5200, 9, null, 'pending'),
                                (3, 6620, 8, null, 'pending'),
                                (4, 5520, 8, null, 'pending'),
                                (5, 5004, 11, null, 'pending'),
                                (6, 5004, 11, null, 'pending'),
                                (7, 6620, 8, null, 'pending');

