DROP USER IF EXISTS admin;
DROP USER IF EXISTS professor;
DROP USER IF EXISTS student;

CREATE USER admin WITH SUPERUSER CREATE ROLE PASSWORD 'admin';
CREATE USER professor WITH PASSWORD 'professor';
CREATE USER student WITH PASSWORD 'student';

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE users, exams, tests, registrations, sessions_tests, sessions, professors_test, students_exams TO admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE exams, tests, registrations, sessions_tests, sessions, professors_test, students_exams TO professor;
GRANT SELECT ON TABLE exams, tests, registrations, sessions_tests, sessions, professors_test TO student; 

--CREATE USER superadmin WITH PASSWORD 'admin' CREATEDB;
--ALTER USER superadmin WITH SUPERUSER;
--ALTER USER superadmin WITH CREATEROLE;

--GRANT superusers TO superadmin;



--CREATE USER your_professor_username WITH PASSWORD 'your_password';
--ALTER USER your_professor_username WITH ROLE professor;

--CREATE USER your_student_username WITH PASSWORD 'your_password';
--ALTER USER your_student_username WITH ROLE student;