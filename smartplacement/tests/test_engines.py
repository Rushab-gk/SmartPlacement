import unittest
from services.eligibility import EligibilityEngine
from services.skill_gap import SkillGapAnalyzer
from services.recommendation import RecommendationEngine
from services.readiness import ReadinessCalculator

class TestPlacementEngines(unittest.TestCase):

    def test_eligibility_engine_eligible(self):
        student = {
            'cgpa': 8.5,
            'tenth_percentage': 85.0,
            'twelfth_percentage': 82.0,
            'diploma_percentage': None,
            'active_backlogs': 0,
            'graduation_year': 2026,
            'branch_id': 1
        }
        criteria = {
            'minimum_cgpa': 7.5,
            'minimum_tenth': 60.0,
            'minimum_twelfth': 60.0,
            'minimum_diploma': 0.0,
            'maximum_backlogs': 0,
            'graduation_year': 2026
        }
        allowed_branches = [1, 2, 3]

        res = EligibilityEngine.check_eligibility(student, criteria, allowed_branches)
        self.assertTrue(res['is_eligible'])

    def test_eligibility_engine_cgpa_failure(self):
        student = {
            'cgpa': 6.8,
            'tenth_percentage': 85.0,
            'twelfth_percentage': 82.0,
            'diploma_percentage': None,
            'active_backlogs': 0,
            'graduation_year': 2026,
            'branch_id': 1
        }
        criteria = {
            'minimum_cgpa': 7.5,
            'minimum_tenth': 60.0,
            'minimum_twelfth': 60.0,
            'minimum_diploma': 0.0,
            'maximum_backlogs': 0,
            'graduation_year': 2026
        }
        allowed_branches = [1, 2]

        res = EligibilityEngine.check_eligibility(student, criteria, allowed_branches)
        self.assertFalse(res['is_eligible'])
        self.assertIn("Minimum CGPA required", res['reasons'][0])

    def test_skill_gap_analyzer(self):
        student_skill_ids = {1, 4, 5} # Python, SQL, HTML
        drive_skills = [
            {'skill_id': 1, 'skill_name': 'Python', 'importance': 'Mandatory'},
            {'skill_id': 4, 'skill_name': 'SQL', 'importance': 'Mandatory'},
            {'skill_id': 8, 'skill_name': 'DSA', 'importance': 'Mandatory'},
            {'skill_id': 2, 'skill_name': 'Java', 'importance': 'Preferred'}
        ]

        res = SkillGapAnalyzer.analyze(student_skill_ids, drive_skills)
        self.assertEqual(res['match_percentage'], 50.0)
        self.assertEqual(len(res['matched_skills']), 2)
        self.assertEqual(res['missing_mandatory'][0]['name'], 'DSA')
        self.assertEqual(res['missing_preferred'][0]['name'], 'Java')

    def test_readiness_calculator(self):
        student = {
            'cgpa': 8.0,
            'dsa_proficiency': 'Intermediate',
            'projects_count': 2,
            'certifications_count': 1,
            'aptitude_score': 80.0
        }
        skill_count = 4

        res = ReadinessCalculator.calculate(student, skill_count)
        # Score calculation check:
        # CGPA: (8/10)*25 = 20
        # Skills: 4*5 = 20
        # DSA: Intermediate = 14
        # Projects: 2*5 = 10
        # Certs: 1*5 = 5
        # Aptitude: (80/100)*5 = 4
        # Total = 20 + 20 + 14 + 10 + 5 + 4 = 73.0
        self.assertEqual(res['readiness_score'], 73.0)

if __name__ == '__main__':
    unittest.main()
