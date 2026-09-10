import os
import unittest

TEST_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'test_smartplacement.sqlite')
os.environ['SMARTPLACEMENT_DB_PATH'] = TEST_DB_PATH

def setUpModule():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

def tearDownModule():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

from app import app
from services.db import fetch_one, fetch_all

class TestSmartPlacementFullApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'testing_key'
        self.client = app.test_client()
        from services.db import execute_query, fetch_one, init_sqlite_db
        init_sqlite_db()
        execute_query("DELETE FROM students WHERE email = 'teststudent@college.edu' OR usn_or_roll = '1VA22CS999'")
        execute_query("INSERT OR IGNORE INTO companies (company_id, company_name, industry, description, website, headquarters) VALUES (1, 'TechCorp Systems', 'IT Services', 'Desc', 'https://techcorp.example.com', 'Bengaluru')")
        execute_query("INSERT OR IGNORE INTO placement_drives (drive_id, company_id, placement_year, job_role, package_ctc, vacancies, drive_date, application_deadline, status) VALUES (1, 1, 2026, 'Software Engineer Trainee', 7.50, 10, '2026-10-15', '2026-10-10', 'Upcoming')")
        execute_query("INSERT OR IGNORE INTO eligibility_criteria (drive_id, minimum_cgpa, minimum_tenth, minimum_twelfth, maximum_backlogs, graduation_year) VALUES (1, 7.0, 60.0, 60.0, 0, 2026)")
        execute_query("INSERT OR IGNORE INTO drive_branches (drive_id, branch_id) VALUES (1, 1)")

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Campus Placement Intelligence', response.data)

    def test_auth_login_render(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account Login', response.data)

    def test_admin_login(self):
        response = self.client.post('/login', data={
            'email': 'admin@college.edu',
            'password': 'admin123',
            'user_type': 'admin'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Placement Cell Admin Portal', response.data)

    def test_student_registration_and_flow(self):
        # 1. Register student
        reg_resp = self.client.post('/register', data={
            'name': 'Test Student',
            'usn_or_roll': '1VA22CS999',
            'email': 'teststudent@college.edu',
            'password': 'password123',
            'branch_id': 1,
            'graduation_year': 2026,
            'cgpa': 8.50,
            'tenth_percentage': 88.0,
            'twelfth_percentage': 85.0,
            'active_backlogs': 0
        }, follow_redirects=True)
        self.assertEqual(reg_resp.status_code, 200)
        self.assertIn(b'Welcome, Test Student!', reg_resp.data)

        # 2. View Student Dashboard
        dash_resp = self.client.get('/student/dashboard')
        self.assertEqual(dash_resp.status_code, 200)
        self.assertIn(b'Placement Readiness', dash_resp.data)

        # 3. View Placement Drives Directory
        drives_resp = self.client.get('/drives')
        self.assertEqual(drives_resp.status_code, 200)
        self.assertIn(b'TechCorp Systems', drives_resp.data)

        # 4. View Company Detail
        detail_resp = self.client.get('/drives/1')
        self.assertEqual(detail_resp.status_code, 200)
        self.assertIn(b'Software Engineer Trainee', detail_resp.data)

        # 5. View Recommendations
        recom_resp = self.client.get('/recommendations')
        self.assertEqual(recom_resp.status_code, 200)
        self.assertIn(b'Ranked Company Recommendations', recom_resp.data)

        # 6. View Skill Gap
        gap_resp = self.client.get('/skill_gap/1')
        self.assertEqual(gap_resp.status_code, 200)
        self.assertIn(b'Skill Gap Analysis', gap_resp.data)

    def test_eligibility_checker_post(self):
        resp = self.client.post('/eligibility', data={
            'drive_id': 1,
            'branch_id': 1,
            'cgpa': 8.5,
            'tenth_percentage': 85.0,
            'twelfth_percentage': 80.0,
            'active_backlogs': 0,
            'graduation_year': 2026
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Evaluation Result', resp.data)

if __name__ == '__main__':
    unittest.main()
