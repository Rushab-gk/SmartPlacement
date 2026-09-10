from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from routes.auth import login_required
from services.db import fetch_one, fetch_all
from services.eligibility import EligibilityEngine
from services.skill_gap import SkillGapAnalyzer

company_bp = Blueprint('company', __name__, url_prefix='/drives')

@company_bp.route('/', strict_slashes=False)
@company_bp.route('', strict_slashes=False)
@login_required
def list_drives():
    # Filtering query parameters
    selected_branch = request.args.get('branch', type=int)
    min_package = request.args.get('min_ctc', type=float)
    max_cgpa_req = request.args.get('max_cgpa', type=float)
    search_query = request.args.get('q', '').strip()
    selected_month = request.args.get('month', '').strip()

    sql = """
        SELECT d.*, c.company_name, c.industry, c.website,
               ec.minimum_cgpa, ec.minimum_tenth, ec.minimum_twelfth, ec.maximum_backlogs, ec.graduation_year
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.company_id
        LEFT JOIN eligibility_criteria ec ON d.drive_id = ec.drive_id
        WHERE 1=1
    """
    params = []

    if search_query:
        sql += " AND (c.company_name LIKE %s OR d.job_role LIKE %s OR c.industry LIKE %s)"
        pattern = f"%{search_query}%"
        params.extend([pattern, pattern, pattern])

    if min_package:
        sql += " AND d.package_ctc >= %s"
        params.append(min_package)

    if max_cgpa_req:
        sql += " AND ec.minimum_cgpa <= %s"
        params.append(max_cgpa_req)

    if selected_branch:
        sql += " AND d.drive_id IN (SELECT drive_id FROM drive_branches WHERE branch_id = %s)"
        params.append(selected_branch)

    if selected_month:
        sql += " AND (d.drive_date LIKE %s)"
        params.append(f"{selected_month}%")

    sql += " ORDER BY d.drive_date ASC"

    drives = fetch_all(sql, params)
    branches = fetch_all("SELECT * FROM branches ORDER BY branch_name ASC")
    months_rows = fetch_all("SELECT DISTINCT SUBSTR(drive_date, 1, 7) AS month_val FROM placement_drives ORDER BY month_val ASC")
    available_months = [m['month_val'] for m in months_rows if m.get('month_val')]

    # If logged in as student, fetch eligibility status for each drive
    student = None
    student_skills = set()
    user_bookmarks = set()
    if session.get('role') == 'student':
        student_id = session['user_id']
        student = fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
        s_skills = fetch_all("SELECT skill_id FROM student_skills WHERE student_id = %s", (student_id,))
        student_skills = {s['skill_id'] for s in s_skills}
        b_marks = fetch_all("SELECT drive_id FROM bookmarks WHERE student_id = %s", (student_id,))
        user_bookmarks = {b['drive_id'] for b in b_marks}

    evaluated_drives = []
    for drive in drives:
        allowed_branches = [b['branch_id'] for b in fetch_all("SELECT branch_id FROM drive_branches WHERE drive_id = %s", (drive['drive_id'],))]
        req_skills = fetch_all("""
            SELECT sk.skill_id, sk.skill_name, ds.importance 
            FROM drive_skills ds 
            JOIN skills sk ON ds.skill_id = sk.skill_id 
            WHERE ds.drive_id = %s
        """, (drive['drive_id'],))

        is_eligible = None
        reasons = []
        skill_gap = None

        if student:
            criteria = {
                'minimum_cgpa': drive.get('minimum_cgpa', 0.0),
                'minimum_tenth': drive.get('minimum_tenth', 0.0),
                'minimum_twelfth': drive.get('minimum_twelfth', 0.0),
                'minimum_diploma': drive.get('minimum_diploma', 0.0),
                'maximum_backlogs': drive.get('maximum_backlogs', 0),
                'graduation_year': drive.get('graduation_year', 0)
            }
            elig_res = EligibilityEngine.check_eligibility(student, criteria, allowed_branches)
            is_eligible = elig_res['is_eligible']
            reasons = elig_res['reasons']
            skill_gap = SkillGapAnalyzer.analyze(student_skills, req_skills)

        evaluated_drives.append({
            'drive': drive,
            'skills': req_skills,
            'is_eligible': is_eligible,
            'reasons': reasons,
            'skill_gap': skill_gap,
            'is_bookmarked': drive['drive_id'] in user_bookmarks
        })

    return render_template(
        'company/list.html',
        drives=evaluated_drives,
        branches=branches,
        selected_branch=selected_branch,
        min_package=min_package,
        max_cgpa=max_cgpa_req,
        search_query=search_query,
        selected_month=selected_month,
        available_months=available_months
    )

@company_bp.route('/<int:drive_id>')
@login_required
def detail(drive_id):
    drive = fetch_one("""
        SELECT d.*, c.company_name, c.industry, c.description AS company_desc, c.website, c.headquarters,
               ec.minimum_cgpa, ec.minimum_tenth, ec.minimum_twelfth, ec.minimum_diploma, ec.maximum_backlogs, ec.graduation_year, ec.other_requirements
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.company_id
        LEFT JOIN eligibility_criteria ec ON d.drive_id = ec.drive_id
        WHERE d.drive_id = %s
    """, (drive_id,))

    if not drive:
        flash('Placement drive not found.', 'danger')
        return redirect(url_for('company.list_drives'))

    allowed_branches = fetch_all("""
        SELECT b.branch_name, b.branch_code 
        FROM drive_branches db 
        JOIN branches b ON db.branch_id = b.branch_id 
        WHERE db.drive_id = %s
    """, (drive_id,))

    req_skills = fetch_all("""
        SELECT sk.skill_id, sk.skill_name, ds.importance 
        FROM drive_skills ds 
        JOIN skills sk ON ds.skill_id = sk.skill_id 
        WHERE ds.drive_id = %s
    """, (drive_id,))

    rounds = fetch_all("""
        SELECT * FROM placement_rounds 
        WHERE drive_id = %s 
        ORDER BY round_number ASC
    """, (drive_id,))

    eligibility_info = None
    skill_analysis = None
    if session.get('role') == 'student':
        student_id = session['user_id']
        student = fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
        if student:
            s_skills = fetch_all("SELECT skill_id FROM student_skills WHERE student_id = %s", (student_id,))
            student_skills = {s['skill_id'] for s in s_skills}
            
            branch_ids = [b['branch_id'] for b in fetch_all("SELECT branch_id FROM drive_branches WHERE drive_id = %s", (drive_id,))]
            criteria = {
                'minimum_cgpa': drive.get('minimum_cgpa', 0.0),
                'minimum_tenth': drive.get('minimum_tenth', 0.0),
                'minimum_twelfth': drive.get('minimum_twelfth', 0.0),
                'minimum_diploma': drive.get('minimum_diploma', 0.0),
                'maximum_backlogs': drive.get('maximum_backlogs', 0),
                'graduation_year': drive.get('graduation_year', 0)
            }
            eligibility_info = EligibilityEngine.check_eligibility(student, criteria, branch_ids)
            skill_analysis = SkillGapAnalyzer.analyze(student_skills, req_skills)

    return render_template(
        'company/detail.html',
        drive=drive,
        allowed_branches=allowed_branches,
        req_skills=req_skills,
        rounds=rounds,
        eligibility_info=eligibility_info,
        skill_analysis=skill_analysis
    )
