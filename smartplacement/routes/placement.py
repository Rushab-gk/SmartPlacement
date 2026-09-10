from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from routes.auth import login_required, student_required
from services.db import fetch_one, fetch_all
from services.eligibility import EligibilityEngine
from services.skill_gap import SkillGapAnalyzer
from services.recommendation import RecommendationEngine

placement_bp = Blueprint('placement', __name__)

@placement_bp.route('/recommendations')
@student_required
def recommendations():
    student_id = session['user_id']
    student = fetch_one("SELECT s.*, b.branch_name FROM students s JOIN branches b ON s.branch_id = b.branch_id WHERE s.student_id = %s", (student_id,))
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('auth.login'))
    skills = fetch_all("SELECT skill_id FROM student_skills WHERE student_id = %s", (student_id,))
    student_skill_ids = {s['skill_id'] for s in skills}

    drives_rows = fetch_all("""
        SELECT d.*, c.company_name, c.industry, ec.minimum_cgpa, ec.minimum_tenth, ec.minimum_twelfth, ec.minimum_diploma, ec.maximum_backlogs, ec.graduation_year
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.company_id
        LEFT JOIN eligibility_criteria ec ON d.drive_id = ec.drive_id
        WHERE d.status = 'Upcoming'
    """)

    drives_data = []
    for d in drives_rows:
        allowed_branches = [b['branch_id'] for b in fetch_all("SELECT branch_id FROM drive_branches WHERE drive_id = %s", (d['drive_id'],))]
        req_skills = fetch_all("""
            SELECT sk.skill_id, sk.skill_name, ds.importance 
            FROM drive_skills ds 
            JOIN skills sk ON ds.skill_id = sk.skill_id 
            WHERE ds.drive_id = %s
        """, (d['drive_id'],))

        criteria = {
            'minimum_cgpa': d.get('minimum_cgpa', 0.0),
            'minimum_tenth': d.get('minimum_tenth', 0.0),
            'minimum_twelfth': d.get('minimum_twelfth', 0.0),
            'minimum_diploma': d.get('minimum_diploma', 0.0),
            'maximum_backlogs': d.get('maximum_backlogs', 0),
            'graduation_year': d.get('graduation_year', 0)
        }

        drives_data.append({
            'drive': d,
            'criteria': criteria,
            'branches': allowed_branches,
            'skills': req_skills
        })

    ranked_drives = RecommendationEngine.rank_drives(student, student_skill_ids, drives_data)
    return render_template('student/recommendations.html', student=student, ranked_drives=ranked_drives)

@placement_bp.route('/skill_gap/<int:drive_id>')
@student_required
def skill_gap(drive_id):
    student_id = session['user_id']
    student = fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
    s_skills = fetch_all("SELECT skill_id FROM student_skills WHERE student_id = %s", (student_id,))
    student_skill_ids = {s['skill_id'] for s in s_skills}

    drive = fetch_one("""
        SELECT d.*, c.company_name, c.industry 
        FROM placement_drives d 
        JOIN companies c ON d.company_id = c.company_id 
        WHERE d.drive_id = %s
    """, (drive_id,))

    if not drive:
        flash('Drive not found.', 'danger')
        return redirect(url_for('company.list_drives'))

    req_skills = fetch_all("""
        SELECT sk.skill_id, sk.skill_name, ds.importance 
        FROM drive_skills ds 
        JOIN skills sk ON ds.skill_id = sk.skill_id 
        WHERE ds.drive_id = %s
    """, (drive_id,))

    analysis = SkillGapAnalyzer.analyze(student_skill_ids, req_skills)
    return render_template('student/skill_gap.html', drive=drive, analysis=analysis)

@placement_bp.route('/eligibility', methods=['GET', 'POST'])
def eligibility_checker():
    drives = fetch_all("""
        SELECT d.drive_id, c.company_name, d.job_role, d.package_ctc 
        FROM placement_drives d 
        JOIN companies c ON d.company_id = c.company_id 
        WHERE d.status = 'Upcoming'
        ORDER BY c.company_name ASC
    """)
    branches = fetch_all("SELECT * FROM branches ORDER BY branch_name ASC")

    result = None
    selected_drive_id = None

    if request.method == 'POST':
        selected_drive_id = request.form.get('drive_id', type=int)
        
        # Student inputs for check
        student_input = {
            'cgpa': request.form.get('cgpa', type=float),
            'tenth_percentage': request.form.get('tenth_percentage', type=float),
            'twelfth_percentage': request.form.get('twelfth_percentage', type=float),
            'diploma_percentage': request.form.get('diploma_percentage', type=float),
            'active_backlogs': request.form.get('active_backlogs', type=int),
            'graduation_year': request.form.get('graduation_year', type=int),
            'branch_id': request.form.get('branch_id', type=int)
        }

        drive = fetch_one("""
            SELECT d.*, c.company_name, ec.* 
            FROM placement_drives d 
            JOIN companies c ON d.company_id = c.company_id 
            JOIN eligibility_criteria ec ON d.drive_id = ec.drive_id 
            WHERE d.drive_id = %s
        """, (selected_drive_id,))

        if drive:
            allowed_branches = [b['branch_id'] for b in fetch_all("SELECT branch_id FROM drive_branches WHERE drive_id = %s", (selected_drive_id,))]
            criteria = {
                'minimum_cgpa': drive.get('minimum_cgpa', 0.0),
                'minimum_tenth': drive.get('minimum_tenth', 0.0),
                'minimum_twelfth': drive.get('minimum_twelfth', 0.0),
                'minimum_diploma': drive.get('minimum_diploma', 0.0),
                'maximum_backlogs': drive.get('maximum_backlogs', 0),
                'graduation_year': drive.get('graduation_year', 0)
            }
            res = EligibilityEngine.check_eligibility(student_input, criteria, allowed_branches)
            result = {
                'drive': drive,
                'is_eligible': res['is_eligible'],
                'reasons': res['reasons']
            }

    return render_template(
        'company/eligibility_checker.html',
        drives=drives,
        branches=branches,
        result=result,
        selected_drive_id=selected_drive_id
    )
