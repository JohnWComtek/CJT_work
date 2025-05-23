from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import Job, User, Client, JobImage, db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

jobs_bp = Blueprint('jobs', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@jobs_bp.route('/jobs')
@login_required
def index():
    jobs = Job.query.all() if current_user.has_role('admin') else Job.query.filter_by(assigned_to=current_user).all()
    return render_template('jobs/index.html', jobs=jobs)

@jobs_bp.route('/jobs/new', methods=['GET', 'POST'])
@login_required
def new_job():
    if request.method == 'POST':
        # Get client or create new one
        client_id = request.form.get('client_id')
        if client_id:
            client = Client.query.get(client_id)
        else:
            # Create new client if client info is provided
            if request.form.get('client_name'):
                client = Client(
                    name=request.form['client_name'],
                    email=request.form.get('client_email'),
                    phone=request.form.get('client_phone'),
                    address=request.form.get('location')
                )
                db.session.add(client)
                db.session.commit()
            else:
                client = None

        job = Job(
            title=request.form['title'],
            description=request.form['description'],
            status=request.form['status'],
            scheduled_date=datetime.strptime(request.form['scheduled_date'], '%Y-%m-%d').date() if request.form['scheduled_date'] else None,
            scheduled_time=datetime.strptime(request.form['scheduled_time'], '%H:%M').time() if request.form['scheduled_time'] else None,
            estimated_duration=float(request.form['estimated_duration']) if request.form['estimated_duration'] else None,
            client_id=client.id if client else None,
            location=request.form['location'],
            priority=request.form['priority'],
            materials_needed=request.form['materials_needed'],
            estimated_cost=float(request.form['estimated_cost']) if request.form['estimated_cost'] else None,
            notes=request.form['notes'],
            created_by_id=current_user.id
        )
        
        if 'assigned_to' in request.form:
            job.assigned_to_id = int(request.form['assigned_to'])
            
        db.session.add(job)
        db.session.commit()

        # Handle image uploads
        if 'images' in request.files:
            uploaded_files = request.files.getlist('images')
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Create unique filename
                    base, ext = os.path.splitext(filename)
                    filename = f"{base}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{ext}"
                    
                    # Ensure upload directory exists
                    upload_dir = os.path.join(current_app.root_path, 'static', 'job_images')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    
                    # Create JobImage record
                    image = JobImage(
                        filename=filename,
                        description=request.form.get('image_description', ''),
                        job_id=job.id
                    )
                    db.session.add(image)
            
            db.session.commit()

        flash('Job created successfully!')
        return redirect(url_for('jobs.index'))
        
    users = User.query.all()
    clients = Client.query.order_by(Client.name).all()
    return render_template('jobs/new.html', users=users, clients=clients)

@jobs_bp.route('/jobs/<int:job_id>')
@login_required
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('jobs/view.html', job=job)

@jobs_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        # Update client information
        client_id = request.form.get('client_id')
        if client_id:
            job.client_id = int(client_id)
        elif request.form.get('client_name'):
            # Create new client if client info is provided
            client = Client(
                name=request.form['client_name'],
                email=request.form.get('client_email'),
                phone=request.form.get('client_phone'),
                address=request.form.get('location')
            )
            db.session.add(client)
            db.session.commit()
            job.client_id = client.id

        job.title = request.form['title']
        job.description = request.form['description']
        job.status = request.form['status']
        job.scheduled_date = datetime.strptime(request.form['scheduled_date'], '%Y-%m-%d').date() if request.form['scheduled_date'] else None
        job.scheduled_time = datetime.strptime(request.form['scheduled_time'], '%H:%M').time() if request.form['scheduled_time'] else None
        job.estimated_duration = float(request.form['estimated_duration']) if request.form['estimated_duration'] else None
        job.location = request.form['location']
        job.priority = request.form['priority']
        job.materials_needed = request.form['materials_needed']
        job.estimated_cost = float(request.form['estimated_cost']) if request.form['estimated_cost'] else None
        job.notes = request.form['notes']
        
        if 'assigned_to' in request.form:
            job.assigned_to_id = int(request.form['assigned_to'])

        # Handle image uploads
        if 'images' in request.files:
            uploaded_files = request.files.getlist('images')
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Create unique filename
                    base, ext = os.path.splitext(filename)
                    filename = f"{base}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{ext}"
                    
                    # Ensure upload directory exists
                    upload_dir = os.path.join(current_app.root_path, 'static', 'job_images')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    
                    # Create JobImage record
                    image = JobImage(
                        filename=filename,
                        description=request.form.get('image_description', ''),
                        job_id=job.id
                    )
                    db.session.add(image)
            
        db.session.commit()
        flash('Job updated successfully!')
        return redirect(url_for('jobs.view_job', job_id=job.id))
        
    users = User.query.all()
    clients = Client.query.order_by(Client.name).all()
    return render_template('jobs/edit.html', job=job, users=users, clients=clients)

@jobs_bp.route('/jobs/<int:job_id>/status', methods=['POST'])
@login_required
def update_status(job_id):
    job = Job.query.get_or_404(job_id)
    new_status = request.form.get('status')
    if new_status:
        job.update_status(new_status)
        flash('Job status updated successfully!')
    return redirect(url_for('jobs.view_job', job_id=job.id))

@jobs_bp.route('/jobs/<int:job_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(job_id, image_id):
    image = JobImage.query.get_or_404(image_id)
    if image.job_id != job_id:
        flash('Invalid image ID for this job.')
        return redirect(url_for('jobs.view_job', job_id=job_id))
    
    # Delete the file
    file_path = os.path.join(current_app.root_path, 'static', 'job_images', image.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete the database record
    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully!')
    return redirect(url_for('jobs.view_job', job_id=job_id)) 