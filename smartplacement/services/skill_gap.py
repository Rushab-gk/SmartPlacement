class SkillGapAnalyzer:
    """
    Skill gap analysis module comparing student skill IDs against drive required skills.
    Categorizes skills into Matched, Missing Mandatory, and Missing Preferred.
    """
    @staticmethod
    def analyze(student_skill_ids: set, drive_skills: list) -> dict:
        """
        student_skill_ids: set of skill_ids possessed by student
        drive_skills: list of dicts [{'skill_id': 1, 'skill_name': 'Python', 'importance': 'Mandatory'}, ...]
        """
        matched_skills = []
        missing_mandatory = []
        missing_preferred = []

        for item in drive_skills:
            s_id = item.get('skill_id')
            s_name = item.get('skill_name', f"Skill #{s_id}")
            importance = item.get('importance', 'Mandatory')

            if s_id in student_skill_ids:
                matched_skills.append({'id': s_id, 'name': s_name, 'importance': importance})
            else:
                if importance == 'Mandatory':
                    missing_mandatory.append({'id': s_id, 'name': s_name})
                else:
                    missing_preferred.append({'id': s_id, 'name': s_name})

        total_skills = len(drive_skills)
        match_percentage = (len(matched_skills) / total_skills * 100.0) if total_skills > 0 else 100.0

        recommendations = []
        if missing_mandatory:
            skills_str = ", ".join([s['name'] for s in missing_mandatory])
            recommendations.append(f"Focus urgently on core mandatory skills: {skills_str}.")
        if missing_preferred:
            skills_str = ", ".join([s['name'] for s in missing_preferred])
            recommendations.append(f"Enhance your candidate profile by learning preferred skills: {skills_str}.")
        if match_percentage >= 80.0 and not missing_mandatory:
            recommendations.append("Your technical skill set aligns very strongly with this job role!")

        return {
            "match_percentage": round(match_percentage, 1),
            "matched_skills": matched_skills,
            "missing_mandatory": missing_mandatory,
            "missing_preferred": missing_preferred,
            "recommendations": recommendations
        }
