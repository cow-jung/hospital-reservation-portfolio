SELECT * FROM hospital_project.doctors;

update doctors
set photo = 'images/doctors/김민준.jpg'
where doctor_id = 1;

update doctors
set photo = 'images/doctors/이서연.jpg'
where doctor_id = 2;

update doctors
set photo = 'images/doctors/박지훈.jpg'
where doctor_id = 3;

update doctors
set photo = 'images/doctors/최유진.jpg'
where doctor_id = 4;

update doctors
set photo = 'images/doctors/정하은.jpg'
where doctor_id = 5;

update doctors
set photo = 'images/doctors/강도윤.jpg'
where doctor_id = 6;

update doctors
set photo = 'images/doctors/윤서아.jpg'
where doctor_id = 7;

update doctors
set photo = 'images/doctors/임재현.jpg'
where doctor_id = 8;

update doctors
set photo = 'images/doctors/한소율.jpg'
where doctor_id = 9;

update doctors
set photo = 'images/doctors/오준서.jpg'
where doctor_id = 10;

ALTER TABLE doctors
ADD COLUMN saturday_available TINYINT(1) NOT NULL DEFAULT 1;

UPDATE doctors
SET saturday_available = 0
WHERE doctor_id in (1, 3, 4, 6, 7, 9);