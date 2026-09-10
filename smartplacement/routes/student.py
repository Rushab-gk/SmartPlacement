import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from routes.auth import student_required
from services.db import fetch_one, fetch_all, execute_query
from services.readiness import ReadinessCalculator
from services.recommendation import RecommendationEngine

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student_id = session['user_id']
    
    # 1. Fetch Student Data
    student = fetch_one("""
        SELECT s.*, b.branch_name, b.branch_code 
        FROM students s 
        JOIN branches b ON s.branch_id = b.branch_id 
        WHERE s.student_id = %s
    """, (student_id,))
    if not student:
        flash('Student record not found.', 'danger')
        return redirect(url_for('auth.login'))

    # 2. Fetch Student Skills
    skills = fetch_all("""
        SELECT sk.skill_id, sk.skill_name, ss.proficiency_level
        FROM student_skills ss
        JOIN skills sk ON ss.skill_id = sk.skill_id
        WHERE ss.student_id = %s
    """, (student_id,))
    student_skill_ids = {s['skill_id'] for s in skills}

    # 3. Calculate Readiness Score
    readiness_data = ReadinessCalculator.calculate(student, len(skills))

    # 4. Fetch All Active Placement Drives & Criteria
    drives_rows = fetch_all("""
        SELECT d.*, c.company_name, c.industry, ec.minimum_cgpa, ec.minimum_tenth, ec.minimum_twelfth, ec.minimum_diploma, ec.maximum_backlogs, ec.graduation_year
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.company_id
        LEFT JOIN eligibility_criteria ec ON d.drive_id = ec.drive_id
        WHERE d.status = 'Upcoming'
        ORDER BY d.drive_date ASC
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

    # Rank Drives using Recommendation Engine
    ranked_drives = RecommendationEngine.rank_drives(student, student_skill_ids, drives_data)

    eligible_count = sum(1 for rd in ranked_drives if rd['is_eligible'])
    highest_eligible_ctc = max([rd['package_ctc'] for rd in ranked_drives if rd['is_eligible']], default=0.0)

    return render_template(
        'student/dashboard.html',
        student=student,
        skills=skills,
        readiness=readiness_data,
        ranked_drives=ranked_drives[:5], # Top 5 recommendations
        total_drives=len(drives_rows),
        eligible_count=eligible_count,
        highest_eligible_ctc=highest_eligible_ctc
    )

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student_id = session['user_id']
    branches = fetch_all("SELECT * FROM branches ORDER BY branch_name ASC")
    all_skills = fetch_all("SELECT * FROM skills ORDER BY skill_category ASC, skill_name ASC")

    if request.method == 'POST':
        cgpa = request.form.get('cgpa')
        tenth_percentage = request.form.get('tenth_percentage')
        twelfth_percentage = request.form.get('twelfth_percentage') or None
        diploma_percentage = request.form.get('diploma_percentage') or None
        active_backlogs = request.form.get('active_backlogs', 0)
        dsa_proficiency = request.form.get('dsa_proficiency', 'Intermediate')
        projects_count = request.form.get('projects_count', 0)
        certifications_count = request.form.get('certifications_count', 0)
        aptitude_score = request.form.get('aptitude_score', 0.0)
        selected_skill_ids = request.form.getlist('skills')

        # Update profile
        update_query = """
            UPDATE students 
            SET cgpa = %s, tenth_percentage = %s, twelfth_percentage = %s, diploma_percentage = %s,
                active_backlogs = %s, dsa_proficiency = %s, projects_count = %s, certifications_count = %s, aptitude_score = %s
            WHERE student_id = %s
        """
        execute_query(update_query, (
            cgpa, tenth_percentage, twelfth_percentage, diploma_percentage,
            active_backlogs, dsa_proficiency, projects_count, certifications_count, aptitude_score, student_id
        ))

        # Update Skills
        execute_query("DELETE FROM student_skills WHERE student_id = %s", (student_id,))
        for s_id in selected_skill_ids:
            execute_query("INSERT INTO student_skills (student_id, skill_id, proficiency_level) VALUES (%s, %s, 'Intermediate')", (student_id, s_id))

        flash('Your profile and technical skills have been updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    student = fetch_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
    current_skills = fetch_all("SELECT skill_id FROM student_skills WHERE student_id = %s", (student_id,))
    current_skill_ids = {s['skill_id'] for s in current_skills}

    projects = fetch_all("SELECT * FROM student_projects WHERE student_id = %s ORDER BY created_at DESC", (student_id,))
    certificates = fetch_all("SELECT * FROM student_certificates WHERE student_id = %s ORDER BY upload_date DESC", (student_id,))

    return render_template(
        'student/profile.html',
        student=student,
        branches=branches,
        all_skills=all_skills,
        current_skill_ids=current_skill_ids,
        projects=projects,
        certificates=certificates
    )

@student_bp.route('/skill/add', methods=['POST'])
@student_required
def add_custom_skill():
    student_id = session['user_id']
    skill_name = request.form.get('skill_name', '').strip()
    skill_category = request.form.get('skill_category', 'Technical').strip()

    if not skill_name:
        flash('Please enter a valid skill name.', 'danger')
        return redirect(url_for('student.profile'))

    existing = fetch_one("SELECT skill_id FROM skills WHERE LOWER(skill_name) = LOWER(%s)", (skill_name,))
    if existing:
        skill_id = existing['skill_id']
    else:
        skill_id = execute_query(
            "INSERT INTO skills (skill_name, skill_category) VALUES (%s, %s)",
            (skill_name, skill_category)
        )

    # Attach skill to student profile
    execute_query("INSERT OR IGNORE INTO student_skills (student_id, skill_id, proficiency_level) VALUES (%s, %s, 'Intermediate')", (student_id, skill_id))

    flash(f"Custom skill '{skill_name}' added to your profile!", 'success')
    return redirect(url_for('student.profile'))

@student_bp.route('/project/add', methods=['POST'])
@student_required
def add_project():
    student_id = session['user_id']
    project_title = request.form.get('project_title', '').strip()
    github_url = request.form.get('github_url', '').strip()

    if not project_title or not github_url:
        flash('Please provide both Project Title and GitHub URL.', 'danger')
        return redirect(url_for('student.profile'))

    if not (github_url.startswith('http://') or github_url.startswith('https://')):
        github_url = 'https://' + github_url

    execute_query(
        "INSERT INTO student_projects (student_id, project_title, github_url) VALUES (%s, %s, %s)",
        (student_id, project_title, github_url)
    )

    # Sync projects_count
    count_res = fetch_one("SELECT COUNT(*) AS c FROM student_projects WHERE student_id = %s", (student_id,))
    p_count = count_res['c'] if count_res else 0
    execute_query("UPDATE students SET projects_count = %s WHERE student_id = %s", (p_count, student_id))

    flash('Project added successfully to your profile!', 'success')
    return redirect(url_for('student.profile'))

@student_bp.route('/project/delete/<int:project_id>', methods=['POST'])
@student_required
def delete_project(project_id):
    student_id = session['user_id']
    execute_query("DELETE FROM student_projects WHERE project_id = %s AND student_id = %s", (project_id, student_id))
    
    count_res = fetch_one("SELECT COUNT(*) AS c FROM student_projects WHERE student_id = %s", (student_id,))
    p_count = count_res['c'] if count_res else 0
    execute_query("UPDATE students SET projects_count = %s WHERE student_id = %s", (p_count, student_id))

    flash('Project deleted.', 'info')
    return redirect(url_for('student.profile'))

@student_bp.route('/certificate/upload', methods=['POST'])
@student_required
def upload_certificate():
    student_id = session['user_id']
    certificate_name = request.form.get('certificate_name', '').strip()
    file = request.files.get('certificate_file')

    if not certificate_name or not file or not file.filename:
        flash('Please provide a certificate name and choose a valid file (PDF, PNG, JPG).', 'danger')
        return redirect(url_for('student.profile'))

    allowed_exts = {'pdf', 'png', 'jpg', 'jpeg'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_exts:
        flash('Invalid file format. Allowed formats: PDF, PNG, JPG, JPEG.', 'danger')
        return redirect(url_for('student.profile'))

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'certificates')
    os.makedirs(upload_folder, exist_ok=True)

    filename = f"student_{student_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    rel_path = f"uploads/certificates/{filename}"
    execute_query(
        "INSERT INTO student_certificates (student_id, certificate_name, file_path) VALUES (%s, %s, %s)",
        (student_id, certificate_name, rel_path)
    )

    count_res = fetch_one("SELECT COUNT(*) AS c FROM student_certificates WHERE student_id = %s", (student_id,))
    c_count = count_res['c'] if count_res else 0
    execute_query("UPDATE students SET certifications_count = %s WHERE student_id = %s", (c_count, student_id))

    flash('Certificate uploaded successfully!', 'success')
    return redirect(url_for('student.profile'))

@student_bp.route('/certificate/delete/<int:cert_id>', methods=['POST'])
@student_required
def delete_certificate(cert_id):
    student_id = session['user_id']
    cert = fetch_one("SELECT * FROM student_certificates WHERE certificate_id = %s AND student_id = %s", (cert_id, student_id))
    if cert:
        if cert.get('file_path'):
            full_path = os.path.join(current_app.root_path, 'static', cert['file_path'])
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception:
                    pass
        execute_query("DELETE FROM student_certificates WHERE certificate_id = %s AND student_id = %s", (cert_id, student_id))

    count_res = fetch_one("SELECT COUNT(*) AS c FROM student_certificates WHERE student_id = %s", (student_id,))
    c_count = count_res['c'] if count_res else 0
    execute_query("UPDATE students SET certifications_count = %s WHERE student_id = %s", (c_count, student_id))

    flash('Certificate removed.', 'info')
    return redirect(url_for('student.profile'))

@student_bp.route('/bookmark/<int:drive_id>', methods=['POST'])
@student_required
def toggle_bookmark(drive_id):
    student_id = session['user_id']
    existing = fetch_one("SELECT bookmark_id FROM bookmarks WHERE student_id = %s AND drive_id = %s", (student_id, drive_id))
    if existing:
        execute_query("DELETE FROM bookmarks WHERE student_id = %s AND drive_id = %s", (student_id, drive_id))
        flash('Drive removed from your bookmarks.', 'info')
    else:
        execute_query("INSERT INTO bookmarks (student_id, drive_id) VALUES (%s, %s)", (student_id, drive_id))
        flash('Drive bookmarked successfully!', 'success')
    return redirect(request.referrer or url_for('company.list_drives'))
