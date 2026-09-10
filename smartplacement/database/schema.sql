-- SmartPlacement Database Schema (MySQL 8.0+)
-- 3rd Normal Form (3NF)

CREATE DATABASE IF NOT EXISTS smartplacement_db
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smartplacement_db;

-- Drop tables in reverse foreign key order if re-initializing
DROP TABLE IF EXISTS bookmarks;
DROP TABLE IF EXISTS placement_rounds;
DROP TABLE IF EXISTS drive_skills;
DROP TABLE IF EXISTS drive_branches;
DROP TABLE IF EXISTS eligibility_criteria;
DROP TABLE IF EXISTS placement_drives;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS student_skills;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS branches;
DROP TABLE IF EXISTS admins;

-- 1. Branches Lookup Table
CREATE TABLE branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL UNIQUE,
    branch_code VARCHAR(10) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 2. Skills Lookup Table
CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    skill_category VARCHAR(50) NOT NULL DEFAULT 'Technical'
) ENGINE=InnoDB;

-- 3. Students Table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    usn_or_roll VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    branch_id INT NOT NULL,
    graduation_year INT NOT NULL,
    cgpa DECIMAL(4,2) NOT NULL CHECK (cgpa >= 0.0 AND cgpa <= 10.0),
    tenth_percentage DECIMAL(5,2) NOT NULL CHECK (tenth_percentage >= 0.0 AND tenth_percentage <= 100.0),
    twelfth_percentage DECIMAL(5,2) DEFAULT NULL CHECK (twelfth_percentage >= 0.0 AND twelfth_percentage <= 100.0),
    diploma_percentage DECIMAL(5,2) DEFAULT NULL CHECK (diploma_percentage >= 0.0 AND diploma_percentage <= 100.0),
    active_backlogs INT NOT NULL DEFAULT 0 CHECK (active_backlogs >= 0),
    cleared_backlogs INT NOT NULL DEFAULT 0 CHECK (cleared_backlogs >= 0),
    dsa_proficiency ENUM('Beginner', 'Intermediate', 'Advanced') DEFAULT 'Intermediate',
    projects_count INT NOT NULL DEFAULT 0,
    certifications_count INT NOT NULL DEFAULT 0,
    aptitude_score DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 4. Student Skills Link Table
CREATE TABLE student_skills (
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('Beginner', 'Intermediate', 'Advanced') DEFAULT 'Intermediate',
    PRIMARY KEY (student_id, skill_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Companies Table
CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL UNIQUE,
    industry VARCHAR(100) NOT NULL,
    description TEXT,
    website VARCHAR(255),
    headquarters VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 6. Placement Drives Table
CREATE TABLE placement_drives (
    drive_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    placement_year INT NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    package_ctc DECIMAL(10,2) NOT NULL COMMENT 'Package in LPA',
    vacancies INT DEFAULT 0,
    drive_date DATE NOT NULL,
    application_deadline DATE NOT NULL,
    status ENUM('Upcoming', 'Ongoing', 'Completed', 'Cancelled') DEFAULT 'Upcoming',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Eligibility Criteria Table
CREATE TABLE eligibility_criteria (
    criteria_id INT AUTO_INCREMENT PRIMARY KEY,
    drive_id INT NOT NULL UNIQUE,
    minimum_cgpa DECIMAL(4,2) NOT NULL DEFAULT 0.0,
    minimum_tenth DECIMAL(5,2) NOT NULL DEFAULT 0.0,
    minimum_twelfth DECIMAL(5,2) DEFAULT 0.0,
    minimum_diploma DECIMAL(5,2) DEFAULT 0.0,
    maximum_backlogs INT NOT NULL DEFAULT 0,
    graduation_year INT NOT NULL,
    other_requirements TEXT,
    FOREIGN KEY (drive_id) REFERENCES placement_drives(drive_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. Drive Allowed Branches Table
CREATE TABLE drive_branches (
    drive_id INT NOT NULL,
    branch_id INT NOT NULL,
    PRIMARY KEY (drive_id, branch_id),
    FOREIGN KEY (drive_id) REFERENCES placement_drives(drive_id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 9. Drive Required Skills Table
CREATE TABLE drive_skills (
    drive_id INT NOT NULL,
    skill_id INT NOT NULL,
    importance ENUM('Mandatory', 'Preferred') DEFAULT 'Mandatory',
    PRIMARY KEY (drive_id, skill_id),
    FOREIGN KEY (drive_id) REFERENCES placement_drives(drive_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 10. Placement Selection Rounds Table
CREATE TABLE placement_rounds (
    round_id INT AUTO_INCREMENT PRIMARY KEY,
    drive_id INT NOT NULL,
    round_number INT NOT NULL,
    round_name VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (drive_id) REFERENCES placement_drives(drive_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 11. Student Bookmarks Table
CREATE TABLE bookmarks (
    bookmark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    drive_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (student_id, drive_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (drive_id) REFERENCES placement_drives(drive_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. Placement Cell Administrators Table
CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'Placement Officer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Database Performance Indexes
CREATE INDEX idx_student_academics ON students(branch_id, graduation_year, cgpa);
CREATE INDEX idx_drive_status ON placement_drives(status, drive_date);
