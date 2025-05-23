from flask import Blueprint, request, send_file, render_template, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import os
from utils.export import export_jobs_to_pdf, export_jobs_to_csv, get_filtered_jobs

exports_bp = Blueprint('exports', __name__)

def export_permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not any(current_user.has_role(role) for role in ['admin', 'bookkeeping', 'project_manager']):
            return render_template('errors/403.html'), 403
        return f(*args, **kwargs)
    return decorated_function

@exports_bp.route('/exports')
@login_required
@export_permission_required
def index():
    return render_template('exports/index.html')

@exports_bp.route('/exports/generate', methods=['POST'])
@login_required
@export_permission_required
def generate_export():
    # Get filter parameters
    export_format = request.form.get('format', 'pdf')
    status = request.form.getlist('status')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    # Convert dates if provided
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get filtered jobs
    jobs = get_filtered_jobs(
        status=status if status else None,
        start_date=start_date,
        end_date=end_date
    )
    
    # Create exports directory if it doesn't exist
    exports_dir = os.path.join(current_app.root_path, 'static', 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    status_str = '_'.join(status) if status else 'all'
    
    if export_format == 'pdf':
        filename = os.path.join(exports_dir, f'jobs_{status_str}_{timestamp}.pdf')
        export_jobs_to_pdf(jobs, filename)
    else:  # CSV
        filename = os.path.join(exports_dir, f'jobs_{status_str}_{timestamp}.csv')
        export_jobs_to_csv(jobs, filename)
    
    # Return the file
    return send_file(
        filename,
        as_attachment=True,
        download_name=os.path.basename(filename)
    ) 