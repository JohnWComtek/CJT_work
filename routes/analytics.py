from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import Job, User, Client, db
from datetime import datetime, timedelta
from sqlalchemy import func, extract, desc, and_
from calendar import monthrange

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def index():
    # Get year and month from query parameters, default to current year/month
    year = request.args.get('year', type=int, default=datetime.utcnow().year)
    month = request.args.get('month', type=int, default=datetime.utcnow().month)
    
    # Calculate date ranges for different periods
    today = datetime.utcnow().date()
    start_of_month = datetime(year, month, 1)
    _, days_in_month = monthrange(year, month)
    end_of_month = datetime(year, month, days_in_month)
    
    # Today's stats
    today_stats = db.session.query(
        func.count(Job.id).label('new_jobs'),
        func.count(Job.id).filter(Job.status == 'completed').label('completed_jobs'),
        func.sum(Job.actual_cost).filter(Job.status == 'completed').label('revenue')
    ).filter(
        func.date(Job.created_at) == today
    ).first()

    # This month's stats
    current_month_stats = db.session.query(
        func.count(Job.id).label('total_jobs'),
        func.count(Job.id).filter(Job.status == 'completed').label('completed_jobs'),
        func.sum(Job.actual_cost).filter(Job.status == 'completed').label('total_revenue'),
        func.avg(Job.actual_cost).filter(Job.status == 'completed').label('avg_job_value')
    ).filter(
        Job.created_at.between(start_of_month, end_of_month)
    ).first()

    # Monthly job completion stats
    monthly_stats = db.session.query(
        extract('month', Job.created_at).label('month'),
        func.count(Job.id).label('completed_count'),
        func.sum(Job.actual_cost).filter(Job.status == 'completed').label('total_value'),
        func.avg(Job.actual_cost).filter(Job.status == 'completed').label('avg_value'),
        func.count(Job.id).filter(Job.status == 'completed').label('completed_count')
    ).filter(
        extract('year', Job.created_at) == year
    ).group_by(
        extract('month', Job.created_at)
    ).order_by(
        extract('month', Job.created_at)
    ).all()

    # Performance by technician
    tech_performance = db.session.query(
        User.name,
        func.count(Job.id).label('total_jobs'),
        func.count(Job.id).filter(Job.status == 'completed').label('completed_jobs'),
        func.avg(
            func.extract('epoch', Job.completed_at) - 
            func.extract('epoch', Job.created_at)
        ).label('avg_completion_time'),
        func.sum(Job.actual_cost).filter(Job.status == 'completed').label('total_revenue')
    ).join(User, Job.assigned_to_id == User.id)\
    .filter(Job.created_at.between(start_of_month, end_of_month))\
    .group_by(User.id)\
    .all()

    # Top clients this month
    top_clients = db.session.query(
        Client.name,
        func.count(Job.id).label('total_jobs'),
        func.sum(Job.actual_cost).filter(Job.status == 'completed').label('total_spent')
    ).join(Job, Client.id == Job.client_id)\
    .filter(Job.created_at.between(start_of_month, end_of_month))\
    .group_by(Client.id)\
    .order_by(desc('total_spent'))\
    .limit(5)\
    .all()

    # Job status distribution
    status_distribution = db.session.query(
        Job.status,
        func.count(Job.id).label('count')
    ).filter(Job.created_at.between(start_of_month, end_of_month))\
    .group_by(Job.status)\
    .all()

    # Priority distribution
    priority_distribution = db.session.query(
        Job.priority,
        func.count(Job.id).label('count')
    ).filter(Job.created_at.between(start_of_month, end_of_month))\
    .group_by(Job.priority)\
    .all()

    # Average completion times by priority
    completion_times = db.session.query(
        Job.priority,
        func.avg(
            func.extract('epoch', Job.completed_at) - 
            func.extract('epoch', Job.created_at)
        ).label('avg_time')
    ).filter(
        Job.status == 'completed',
        Job.created_at.between(start_of_month, end_of_month)
    ).group_by(Job.priority)\
    .all()

    # Recent activity
    recent_activity = db.session.query(Job)\
        .filter(Job.created_at.between(start_of_month, end_of_month))\
        .order_by(desc(Job.updated_at))\
        .limit(10)\
        .all()

    return render_template('analytics/index.html',
                         year=year,
                         month=month,
                         today_stats=today_stats,
                         current_month_stats=current_month_stats,
                         monthly_stats=monthly_stats,
                         tech_performance=tech_performance,
                         top_clients=top_clients,
                         status_distribution=status_distribution,
                         priority_distribution=priority_distribution,
                         completion_times=completion_times,
                         recent_activity=recent_activity)

@analytics_bp.route('/analytics/export')
@login_required
def export_data():
    # Add export functionality here
    pass

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