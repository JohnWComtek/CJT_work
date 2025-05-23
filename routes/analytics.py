from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Job, db
from datetime import datetime
from sqlalchemy import func, extract

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def index():
    # Get year and month from query parameters, default to current year/month
    year = request.args.get('year', type=int, default=datetime.utcnow().year)
    month = request.args.get('month', type=int, default=datetime.utcnow().month)

    # Monthly job completion stats
    monthly_stats = db.session.query(
        extract('month', Job.completed_at).label('month'),
        func.count(Job.id).label('completed_count'),
        func.sum(Job.actual_cost).label('total_value')
    ).filter(
        extract('year', Job.completed_at) == year,
        Job.status == 'completed'
    ).group_by(
        extract('month', Job.completed_at)
    ).all()

    # Total jobs stats
    total_stats = db.session.query(
        func.count(Job.id).label('total_jobs'),
        func.count(Job.id).filter(Job.status == 'completed').label('completed_jobs'),
        func.sum(Job.actual_cost).filter(Job.status == 'completed').label('total_revenue')
    ).first()

    # Average completion time
    avg_completion_time = db.session.query(
        func.avg(
            func.extract('epoch', Job.completed_at) - 
            func.extract('epoch', Job.created_at)
        ) / 3600  # Convert to hours
    ).filter(Job.status == 'completed').scalar()

    return render_template('analytics/index.html',
                         year=year,
                         month=month,
                         monthly_stats=monthly_stats,
                         total_stats=total_stats,
                         avg_completion_time=avg_completion_time)

@analytics_bp.route('/completed-jobs')
@login_required
def completed_jobs():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get completed jobs with pagination
    completed_jobs = Job.query.filter_by(status='completed')\
        .order_by(Job.completed_at.desc())\
        .paginate(page=page, per_page=per_page)

    return render_template('analytics/completed_jobs.html', jobs=completed_jobs)

@analytics_bp.route('/job-search')
@login_required
def job_search():
    query = request.args.get('q', '')
    if query:
        jobs = Job.search(query)
    else:
        jobs = []
    
    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([{
            'id': job.id,
            'title': job.title,
            'status': job.status,
            'client_name': job.client.name if job.client else None,
            'scheduled_date': job.scheduled_date.strftime('%Y-%m-%d') if job.scheduled_date else None
        } for job in jobs])
    
    return render_template('analytics/search.html', jobs=jobs, query=query) 