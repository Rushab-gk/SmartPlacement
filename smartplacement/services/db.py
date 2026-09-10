import os
import sqlite3
import logging
import mysql.connector
from mysql.connector import Error as MySQLError
from config import Config

logger = logging.getLogger(__name__)

use_sqlite_fallback = False
db_pool = None
DEFAULT_SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'smartplacement.sqlite')

def get_sqlite_db_path() -> str:
    return os.environ.get('SMARTPLACEMENT_DB_PATH', DEFAULT_SQLITE_DB_PATH)

def init_sqlite_db():
    """Initialize SQLite tables and insert seed data if sqlite file is newly created."""
    conn = sqlite3.connect(get_sqlite_db_path())
    cursor = conn.cursor()
    
    # 1. Branches
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_name TEXT NOT NULL UNIQUE,
        branch_code TEXT NOT NULL UNIQUE
    );""")
    
    # 2. Skills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL UNIQUE,
        skill_category TEXT NOT NULL DEFAULT 'Technical'
    );""")

    # 3. Students
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        usn_or_roll TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        branch_id INTEGER NOT NULL,
        graduation_year INTEGER NOT NULL,
        cgpa REAL NOT NULL,
        tenth_percentage REAL NOT NULL,
        twelfth_percentage REAL,
        diploma_percentage REAL,
        active_backlogs INTEGER NOT NULL DEFAULT 0,
        cleared_backlogs INTEGER NOT NULL DEFAULT 0,
        dsa_proficiency TEXT DEFAULT 'Beginner',
        projects_count INTEGER DEFAULT 0,
        certifications_count INTEGER DEFAULT 0,
        aptitude_score REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (branch_id) REFERENCES branches (branch_id)
    );""")

    # 4. Companies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL UNIQUE,
        industry TEXT NOT NULL,
        description TEXT,
        website TEXT,
        headquarters TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")

    # 5. Student Skills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_skills (
        student_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        proficiency_level TEXT DEFAULT 'Intermediate',
        PRIMARY KEY (student_id, skill_id)
    );""")

    # 6. Placement Drives
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS placement_drives (
        drive_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        placement_year INTEGER NOT NULL,
        job_role TEXT NOT NULL,
        package_ctc REAL NOT NULL,
        vacancies INTEGER NOT NULL DEFAULT 0,
        drive_date TEXT NOT NULL,
        application_deadline TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Upcoming',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies (company_id)
    );""")

    # 7. Eligibility Criteria
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eligibility_criteria (
        criteria_id INTEGER PRIMARY KEY AUTOINCREMENT,
        drive_id INTEGER NOT NULL,
        minimum_cgpa REAL NOT NULL DEFAULT 0.0,
        minimum_tenth REAL NOT NULL DEFAULT 0.0,
        minimum_twelfth REAL DEFAULT 0.0,
        minimum_diploma REAL DEFAULT 0.0,
        maximum_backlogs INTEGER NOT NULL DEFAULT 0,
        graduation_year INTEGER NOT NULL,
        other_requirements TEXT
    );""")

    # 8. Drive Branches
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drive_branches (
        drive_id INTEGER NOT NULL,
        branch_id INTEGER NOT NULL,
        PRIMARY KEY (drive_id, branch_id)
    );""")

    # 9. Drive Skills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drive_skills (
        drive_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        importance TEXT DEFAULT 'Mandatory',
        PRIMARY KEY (drive_id, skill_id)
    );""")

    # 10. Placement Rounds
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS placement_rounds (
        round_id INTEGER PRIMARY KEY AUTOINCREMENT,
        drive_id INTEGER NOT NULL,
        round_number INTEGER NOT NULL,
        round_name TEXT NOT NULL,
        description TEXT
    );""")

    # 11. Bookmarks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        drive_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (student_id, drive_id)
    );""")

    # 12. Admins
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'Placement Officer',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")

    # 13. Student Projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_projects (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        project_title TEXT NOT NULL,
        github_url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")

    # 14. Student Certificates
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_certificates (
        certificate_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        certificate_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")

    cursor.execute("SELECT COUNT(*) FROM branches;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO branches (branch_id, branch_name, branch_code) VALUES (?, ?, ?);", [
            (1, 'Computer Science & Engineering', 'CSE'),
            (2, 'Information Science & Engineering', 'ISE'),
            (3, 'Electronics & Communication Engineering', 'ECE'),
            (4, 'Electrical & Electronics Engineering', 'EEE'),
            (5, 'Mechanical Engineering', 'ME')
        ])

    cursor.execute("SELECT COUNT(*) FROM skills;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO skills (skill_id, skill_name, skill_category) VALUES (?, ?, ?);", [
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
            (12, 'Docker', 'DevOps')
        ])

    cursor.execute("SELECT COUNT(*) FROM admins;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO admins (admin_id, name, email, password_hash, role) VALUES 
        (1, 'Dr. Placement Director', 'admin@college.edu', 'scrypt:32768:8:1$kBcQH6dqdJbCfKbt$1f61f664c7b6198fde6f16ca7c8d1cd70bd5214e65f7353d79a36d9be3b5bfc569fcea29f82a45fc31f2ca5227b34c3d476b4c5e8ccfdd11212ad971e822d00c', 'Placement Director');
        """)

    conn.commit()
    conn.close()

def init_db_pool():
    global db_pool, use_sqlite_fallback
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="smartplacement_pool",
            pool_size=5,
            pool_reset_session=True,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        logger.info("MySQL Connection Pool created successfully.")
    except Exception as e:
        use_sqlite_fallback = True
        logger.warning(f"MySQL unavailable ({e}). Seamlessly switching to local SQLite database fallback.")
        init_sqlite_db()

def _convert_query_to_sqlite(query: str) -> str:
    # Replace MySQL %s parameter placeholders with SQLite ? placeholders
    return query.replace('%s', '?')

from typing import Any, Dict, List, Optional, cast

def fetch_one(query: str, params: Any = ()) -> Optional[Dict[str, Any]]:
    global use_sqlite_fallback
    if use_sqlite_fallback:
        conn = sqlite3.connect(get_sqlite_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(_convert_query_to_sqlite(query), params)
        row = cursor.fetchone()
        res: Optional[Dict[str, Any]] = dict(row) if row else None  # type: ignore[arg-type]
        cursor.close()
        conn.close()
        return res

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return cast(Optional[Dict[str, Any]], result) if isinstance(result, dict) else None
    except MySQLError as e:
        logger.error(f"Database Query Error (fetch_one): {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def fetch_all(query: str, params: Any = ()) -> List[Dict[str, Any]]:
    global use_sqlite_fallback
    if use_sqlite_fallback:
        conn = sqlite3.connect(get_sqlite_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(_convert_query_to_sqlite(query), params)
        rows = cursor.fetchall()
        res: List[Dict[str, Any]] = [dict(r) for r in rows]  # type: ignore[arg-type]
        cursor.close()
        conn.close()
        return res

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        if isinstance(results, list):
            res_list: List[Dict[str, Any]] = [cast(Dict[str, Any], r) for r in results if isinstance(r, dict)]
            return res_list
        return []
    except MySQLError as e:
        logger.error(f"Database Query Error (fetch_all): {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

def execute_query(query: str, params: Any = ()) -> int:
    global use_sqlite_fallback
    if use_sqlite_fallback:
        conn = sqlite3.connect(get_sqlite_db_path())
        cursor = conn.cursor()
        cursor.execute(_convert_query_to_sqlite(query), params)
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return int(last_id) if last_id is not None else 0

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return int(last_id) if last_id is not None else 0
    except MySQLError as e:
        logger.error(f"Database Execution Error: {e}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_db_connection():
    global db_pool
    if db_pool:
        try:
            return db_pool.get_connection()
        except MySQLError:
            pass
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
