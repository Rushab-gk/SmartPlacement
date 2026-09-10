from services.eligibility import EligibilityEngine
from services.skill_gap import SkillGapAnalyzer

class RecommendationEngine:
    """
    Rule-based recommendation engine scoring drives for a student.
    Formula: Score = EligibilityMultiplier * (0.7 * SkillRatio + 0.3 * CGPABufferRatio)
    """
    @staticmethod
    def rank_drives(student: dict, student_skills: set, drives_data: list) -> list:
        ranked_results = []

        for item in drives_data:
            drive = item['drive']
            criteria = item['criteria']
            allowed_branches = item.get('branches', [])
            skills_req = item.get('skills', [])

            # 1. Eligibility Check
            elig = EligibilityEngine.check_eligibility(student, criteria, allowed_branches)
            
            # 2. Skill Gap Check
            skill_analysis = SkillGapAnalyzer.analyze(student_skills, skills_req)
            
            # 3. Score Calculation
            eligibility_mult = 1.0 if elig['is_eligible'] else 0.2
            skill_ratio = skill_analysis['match_percentage'] / 100.0
            
            student_cgpa = float(student.get('cgpa', 0.0))
            min_cgpa = float(criteria.get('minimum_cgpa', 0.0))
            cgpa_diff = max(0.0, student_cgpa - min_cgpa)
            cgpa_buffer_ratio = min(1.0, cgpa_diff / 2.0)
            
            raw_score = (skill_ratio * 70.0) + (cgpa_buffer_ratio * 30.0)
            final_score = round(raw_score * eligibility_mult, 1)

            # Categorization
            if elig['is_eligible'] and final_score >= 75.0:
                category = "Highly Suitable"
            elif elig['is_eligible'] and final_score >= 50.0:
                category = "Suitable"
            else:
                category = "Preparation Required"

            ranked_results.append({
                "drive_id": drive['drive_id'],
                "company_name": drive['company_name'],
                "job_role": drive['job_role'],
                "package_ctc": drive['package_ctc'],
                "final_score": final_score,
                "category": category,
                "is_eligible": elig['is_eligible'],
                "eligibility_reasons": elig['reasons'],
                "skill_match_percentage": skill_analysis['match_percentage'],
                "missing_skills": skill_analysis['missing_mandatory']
            })

        ranked_results.sort(key=lambda x: x['final_score'], reverse=True)
        return ranked_results
