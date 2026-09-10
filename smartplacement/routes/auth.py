from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from services.db import fetch_one, execute_query, fetch_all

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            flash('Access restricted to students only.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Administrator access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    selected_role = request.args.get('role', 'student').strip()
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user_type = request.form.get('user_type', 'student')
        selected_role = user_type

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html', selected_role=selected_role)

        if user_type == 'admin':
            user = fetch_one("SELECT * FROM admins WHERE email = %s", (email,))
            if user and check_password_hash(user['password_hash'], password):
                session.clear()
                session['user_id'] = user['admin_id']
                session['name'] = user['name']
                session['email'] = user['email']
                session['role'] = 'admin'
                flash(f"Welcome back, {user['name']}!", 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid admin email or password.', 'danger')
        else:
            user = fetch_one("SELECT * FROM students WHERE email = %s", (email,))
            if user and check_password_hash(user['password_hash'], password):
                session.clear()
                session['user_id'] = user['student_id']
                session['name'] = user['name']
                session['email'] = user['email']
                session['role'] = 'student'
                flash(f"Welcome back, {user['name']}!", 'success')
                return redirect(url_for('student.dashboard'))
            else:
                flash('Invalid student email or password.', 'danger')

    return render_template('auth/login.html', selected_role=selected_role)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    branches = fetch_all("SELECT * FROM branches ORDER BY branch_name ASC")
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        usn_or_roll = request.form.get('usn_or_roll', '').strip().upper()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        branch_id = request.form.get('branch_id')
        graduation_year = request.form.get('graduation_year')
        cgpa = request.form.get('cgpa', 0.0)
        tenth_percentage = request.form.get('tenth_percentage', 0.0)
        twelfth_percentage = request.form.get('twelfth_percentage') or None
        diploma_percentage = request.form.get('diploma_percentage') or None
        active_backlogs = request.form.get('active_backlogs', 0)

        # Basic Validation
        if not all([name, usn_or_roll, email, password, branch_id, graduation_year]):
            flash('Please fill in all mandatory profile fields.', 'danger')
            return render_template('auth/register.html', branches=branches)

        # Check existing USN / Email
        existing = fetch_one("SELECT student_id FROM students WHERE email = %s OR usn_or_roll = %s", (email, usn_or_roll))
        if existing:
            flash('Email or USN/Roll number is already registered.', 'warning')
            return render_template('auth/register.html', branches=branches)

        password_hash = generate_password_hash(password)

        try:
            query = """
                INSERT INTO students 
                (usn_or_roll, name, email, password_hash, branch_id, graduation_year, cgpa, tenth_percentage, twelfth_percentage, diploma_percentage, active_backlogs)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            student_id = execute_query(query, (
                usn_or_roll, name, email, password_hash, branch_id, graduation_year, cgpa, tenth_percentage, twelfth_percentage, diploma_percentage, active_backlogs
            ))

            session.clear()
            session['user_id'] = student_id
            session['name'] = name
            session['email'] = email
            session['role'] = 'student'
            flash('Registration successful! Welcome to SmartPlacement.', 'success')
            return redirect(url_for('student.dashboard'))
        except Exception as e:
            flash(f'Error creating student profile: {str(e)}', 'danger')

    return render_template('auth/register.html', branches=branches)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
