from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Job

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_jobs = []
    if current_user.has_role('admin'):
        # Admin sees all jobs
        jobs = Job.query.all()
    else:
        # Filter jobs based on user role and status
        if current_user.has_role('bookkeeping'):
            jobs = Job.query.filter_by(status='To be billed').all()
        elif current_user.has_role('sales') or current_user.has_role('project_manager'):
            jobs = Job.query.filter_by(status='quote needed').all()
        elif current_user.has_role('technician'):
            jobs = Job.query.filter_by(status='scheduled', assigned_to=current_user).all()
        else:
            jobs = Job.query.filter_by(assigned_to=current_user).all()

    return render_template('dashboard/index.html', 
                         jobs=jobs,
                         user=current_user)

@dashboard_bp.route('/dashboard/jobs/<status>')
@login_required
def jobs_by_status(status):
    if current_user.has_role('admin'):
        jobs = Job.query.filter_by(status=status).all()
    else:
        jobs = Job.query.filter_by(status=status, assigned_to=current_user).all()
    return render_template('dashboard/jobs.html', jobs=jobs, status=status) 