SELECT * FROM hospital_project.departments;

UPDATE departments
SET dept_image = 'images/departments/internal_medicine.jpg'
WHERE dept_name = '내과';

UPDATE departments
SET dept_image = 'images/departments/orthopedics.jpg'
WHERE dept_name = '정형외과';

UPDATE departments
SET dept_image = 'images/departments/pediatrics.jpg'
WHERE dept_name = '소아청소년과';

UPDATE departments
SET dept_image = 'images/departments/dermatology.jpg'
WHERE dept_name = '피부과';

UPDATE departments
SET dept_image = 'images/departments/dentistry.jpg'
WHERE dept_name = '치과';

SELECT
    dept_id,
    dept_name,
    dept_image
FROM departments;