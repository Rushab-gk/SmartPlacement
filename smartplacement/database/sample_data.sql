USE smartplacement_db;

-- Insert Branches
INSERT INTO branches (branch_id, branch_name, branch_code) VALUES
(1, 'Computer Science & Engineering', 'CSE'),
(2, 'Information Science & Engineering', 'ISE'),
(3, 'Electronics & Communication Engineering', 'ECE'),
(4, 'Electrical & Electronics Engineering', 'EEE'),
(5, 'Mechanical Engineering', 'ME');

-- Insert Skills
INSERT INTO skills (skill_id, skill_name, skill_category) VALUES
(1, 'Python', 'Programming'),
(2, 'Java', 'Programming'),
(3, 'C++', 'Programming'),
(4, 'SQL', 'Database'),
(5, 'HTML/CSS', 'Frontend'),
(6, 'JavaScript', 'Frontend'),
(7, 'Flask', 'Backend'),
(8, 'Data Structures & Algorithms', 'Core CSE'),
(9, 'Operating Systems', 'Core CSE'),
(10, 'Computer Networks', 'Core CSE'),
(11, 'Cloud Computing (AWS/Azure)', 'DevOps'),
(12, 'Docker', 'DevOps');

-- Insert Admin Account (Password: admin123)
-- Hash generated via werkzeug.security: pbkdf2:sha256:600000$04Vb2p5u3W4O...
INSERT INTO admins (admin_id, name, email, password_hash, role) VALUES
(1, 'Dr. Placement Director', 'admin@college.edu', 'pbkdf2:sha256:600000$56qWdYhK9X0M8b4Z$96df06c11dbb5b48db92c3fa50ed49646543b593630ce14ae010bcbeeeefaa0c', 'Placement Director');

-- Insert Sample Companies
INSERT INTO companies (company_id, company_name, industry, description, website, headquarters) VALUES
(1, 'TechCorp Systems', 'IT Services & Consulting', 'Global software services company.', 'https://techcorp.example.com', 'Bengaluru'),
(2, 'CloudMatrix Analytics', 'Product / Cloud', 'Cloud infrastructure and data analytics startup.', 'https://cloudmatrix.example.com', 'Hyderabad'),
(3, 'FinTech Solutions Ltd', 'Financial Technology', 'Enterprise banking & payment processor.', 'https://fintech.example.com', 'Mumbai'),
(4, 'CoreElectro Dynamics', 'Embedded Systems', 'Semiconductor and embedded systems provider.', 'https://coreelectro.example.com', 'Pune');

-- Insert Placement Drives for 2026
INSERT INTO placement_drives (drive_id, company_id, placement_year, job_role, package_ctc, vacancies, drive_date, application_deadline, status) VALUES
(1, 1, 2026, 'Software Engineer Trainee', 7.50, 45, '2026-10-15', '2026-10-05', 'Upcoming'),
(2, 2, 2026, 'Associate Cloud Developer', 12.00, 15, '2026-11-01', '2026-10-20', 'Upcoming'),
(3, 3, 2026, 'Backend Developer (Python/Java)', 9.00, 20, '2026-10-25', '2026-10-12', 'Upcoming'),
(4, 4, 2026, 'Embedded Systems Engineer', 6.50, 10, '2026-11-10', '2026-10-30', 'Upcoming');

-- Insert Eligibility Criteria
INSERT INTO eligibility_criteria (criteria_id, drive_id, minimum_cgpa, minimum_tenth, minimum_twelfth, minimum_diploma, maximum_backlogs, graduation_year, other_requirements) VALUES
(1, 1, 7.00, 60.00, 60.00, 60.00, 0, 2026, 'Strong problem-solving and basic programming skills.'),
(2, 2, 8.00, 75.00, 75.00, 75.00, 0, 2026, 'Must possess core knowledge of Linux, Networking, and DSA.'),
(3, 3, 7.50, 65.00, 65.00, 65.00, 1, 2026, 'Good knowledge of database query optimization and API backend.'),
(4, 4, 6.50, 60.00, 60.00, 60.00, 2, 2026, 'Knowledge of C/C++ and microcontrollers.');

-- Insert Allowed Branches for Drives
INSERT INTO drive_branches (drive_id, branch_id) VALUES
-- Drive 1: TechCorp (CSE, ISE, ECE)
(1, 1), (1, 2), (1, 3),
-- Drive 2: CloudMatrix (CSE, ISE)
(2, 1), (2, 2),
-- Drive 3: FinTech (CSE, ISE, ECE, EEE)
(3, 1), (3, 2), (3, 3), (3, 4),
-- Drive 4: CoreElectro (ECE, EEE, ME)
(4, 3), (4, 4), (4, 5);

-- Insert Drive Required Skills
INSERT INTO drive_skills (drive_id, skill_id, importance) VALUES
-- Drive 1 TechCorp
(1, 1, 'Mandatory'), -- Python
(1, 4, 'Mandatory'), -- SQL
(1, 8, 'Mandatory'), -- DSA
(1, 5, 'Preferred'), -- HTML/CSS
-- Drive 2 CloudMatrix
(2, 1, 'Mandatory'), -- Python
(2, 8, 'Mandatory'), -- DSA
(2, 11, 'Mandatory'),-- Cloud
(2, 12, 'Preferred'),-- Docker
-- Drive 3 FinTech
(3, 2, 'Mandatory'), -- Java
(3, 4, 'Mandatory'), -- SQL
(3, 7, 'Preferred'), -- Flask
-- Drive 4 CoreElectro
(4, 3, 'Mandatory'), -- C++
(4, 9, 'Mandatory'); -- OS

-- Insert Placement Rounds
INSERT INTO placement_rounds (round_id, drive_id, round_number, round_name, description) VALUES
(1, 1, 1, 'Online Aptitude & Coding Test', 'Quantitative aptitude, logical reasoning, and 2 coding problems.'),
(2, 1, 2, 'Technical Interview', 'In-depth evaluation of DSA, DBMS, and OOP concepts.'),
(3, 1, 3, 'HR Interview', 'Culture fit, communication skills, and document verification.'),
(4, 2, 1, 'Advanced DSA Coding Challenge', '3 algorithmic coding questions on platform.'),
(5, 2, 2, 'System Design & Technical Round', 'Discussion on scalable architectures and cloud fundamentals.');
