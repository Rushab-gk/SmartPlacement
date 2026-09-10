class EligibilityEngine:
    """
    Rule-based eligibility evaluation engine.
    Checks CGPA, 10th %, 12th / Diploma %, Backlogs, Graduation Year, and Allowed Branches.
    """
    @staticmethod
    def check_eligibility(student: dict, criteria: dict, allowed_branches: list) -> dict:
        reasons = []
        is_eligible = True

        # 1. CGPA Check
        student_cgpa = float(student.get('cgpa', 0.0))
        min_cgpa = float(criteria.get('minimum_cgpa', 0.0))
        if student_cgpa < min_cgpa:
            is_eligible = False
            reasons.append(f"Minimum CGPA required: {min_cgpa:.2f} (Your CGPA: {student_cgpa:.2f})")

        # 2. 10th Percentage Check
        student_10th = float(student.get('tenth_percentage', 0.0))
        min_10th = float(criteria.get('minimum_tenth', 0.0))
        if student_10th < min_10th:
            is_eligible = False
            reasons.append(f"Minimum 10th percentage required: {min_10th:.1f}% (Your 10th: {student_10th:.1f}%)")

        # 3. 12th / Diploma Check
        student_12th = student.get('twelfth_percentage')
        student_diploma = student.get('diploma_percentage')
        min_12th = float(criteria.get('minimum_twelfth', 0.0))
        min_diploma = float(criteria.get('minimum_diploma', 0.0))

        if student_12th is not None and min_12th > 0:
            if float(student_12th) < min_12th:
                is_eligible = False
                reasons.append(f"Minimum 12th percentage required: {min_12th:.1f}% (Your 12th: {float(student_12th):.1f}%)")
        elif student_diploma is not None and min_diploma > 0:
            if float(student_diploma) < min_diploma:
                is_eligible = False
                reasons.append(f"Minimum Diploma percentage required: {min_diploma:.1f}% (Your Diploma: {float(student_diploma):.1f}%)")

        # 4. Active Backlogs Check
        active_backlogs = int(student.get('active_backlogs', 0))
        max_backlogs = int(criteria.get('maximum_backlogs', 0))
        if active_backlogs > max_backlogs:
            is_eligible = False
            reasons.append(f"Maximum active backlogs allowed: {max_backlogs} (Your Active Backlogs: {active_backlogs})")

        # 5. Graduation Year Check
        student_grad_year = int(student.get('graduation_year', 0))
        target_grad_year = int(criteria.get('graduation_year', 0))
        if target_grad_year > 0 and student_grad_year != target_grad_year:
            is_eligible = False
            reasons.append(f"Target graduation year required: {target_grad_year} (Your Year: {student_grad_year})")

        # 6. Branch Check
        student_branch_id = int(student.get('branch_id', 0))
        allowed_branch_ids = [int(b) for b in allowed_branches]
        if allowed_branch_ids and student_branch_id not in allowed_branch_ids:
            is_eligible = False
            reasons.append("Your academic branch is not eligible for this placement drive.")

        return {
            "is_eligible": is_eligible,
            "reasons": reasons if not is_eligible else ["All academic eligibility criteria satisfied."]
        }
