class ReadinessCalculator:
    """
    Calculates Placement Readiness Score (0-100) based on transparent rule weights:
    - CGPA: 25%
    - Technical Skills count: 25%
    - DSA Proficiency: 20%
    - Projects Count: 15%
    - Certifications: 10%
    - Aptitude Score: 5%
    """
    @staticmethod
    def calculate(student: dict, skill_count: int) -> dict:
        # 1. CGPA Component (Max 25 pts)
        cgpa = float(student.get('cgpa', 0.0))
        cgpa_score = min(25.0, (cgpa / 10.0) * 25.0)

        # 2. Skills Component (Max 25 pts, 5 pts per skill up to 5)
        skill_score = min(25.0, skill_count * 5.0)

        # 3. DSA Proficiency (Max 20 pts)
        dsa_level = student.get('dsa_proficiency', 'Beginner')
        dsa_map = {'Beginner': 8.0, 'Intermediate': 14.0, 'Advanced': 20.0}
        dsa_score = dsa_map.get(dsa_level, 8.0)

        # 4. Projects Count (Max 15 pts, 5 pts per project up to 3)
        projects = int(student.get('projects_count', 0))
        projects_score = min(15.0, projects * 5.0)

        # 5. Certifications (Max 10 pts, 5 pts per cert up to 2)
        certs = int(student.get('certifications_count', 0))
        certs_score = min(10.0, certs * 5.0)

        # 6. Aptitude (Max 5 pts)
        apt_percentage = float(student.get('aptitude_score', 0.0))
        apt_score = min(5.0, (apt_percentage / 100.0) * 5.0)

        total_readiness = round(cgpa_score + skill_score + dsa_score + projects_score + certs_score + apt_score, 1)

        feedback = []
        if cgpa < 7.0:
            feedback.append("Aim to improve your academic CGPA above 7.0 for broader company eligibility.")
        if skill_count < 3:
            feedback.append("Add more technical skills to your profile to increase overall match scores.")
        if dsa_level == 'Beginner':
            feedback.append("Practice Data Structures & Algorithms regularly on LeetCode/HackerRank to reach Intermediate level.")
        if projects < 2:
            feedback.append("Build at least 2 hands-on technical projects to showcase on your resume.")

        return {
            "readiness_score": total_readiness,
            "breakdown": {
                "cgpa_score": round(cgpa_score, 1),
                "skill_score": round(skill_score, 1),
                "dsa_score": round(dsa_score, 1),
                "projects_score": round(projects_score, 1),
                "certs_score": round(certs_score, 1),
                "apt_score": round(apt_score, 1)
            },
            "feedback": feedback if feedback else ["Your profile shows strong overall readiness across all indicators!"]
        }
