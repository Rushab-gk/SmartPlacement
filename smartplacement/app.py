from flask import Flask, render_template, session
from config import Config
from services.db import init_db_pool, fetch_one
from routes.auth import auth_bp
from routes.student import student_bp
from routes.company import company_bp
from routes.admin import admin_bp
from routes.placement import placement_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Database Connection Pool
    init_db_pool()

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(placement_bp)

    @app.route('/')
    def index():
        comp_res = fetch_one("SELECT COUNT(*) AS c FROM companies")
        drive_res = fetch_one("SELECT COUNT(*) AS c FROM placement_drives WHERE status='Upcoming'")
        pkg_res = fetch_one("SELECT MAX(package_ctc) AS m FROM placement_drives")

        stats = {
            'companies': comp_res['c'] if comp_res and 'c' in comp_res else 4,
            'drives': drive_res['c'] if drive_res and 'c' in drive_res else 4,
            'highest_pkg': pkg_res['m'] if pkg_res and 'm' in pkg_res and pkg_res['m'] is not None else 12.0
        }
        return render_template('index.html', stats=stats)

    @app.context_processor
    def inject_user():
        return {
            'current_user_name': session.get('name'),
            'current_user_role': session.get('role')
        }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', custom_error="404 - Page Not Found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('base.html', custom_error="500 - Internal Server Error"), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
