from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', name='fk_user_roles_user_id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', name='fk_user_roles_role_id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128))
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    assigned_jobs = db.relationship('Job', backref='assigned_to', lazy='dynamic', foreign_keys='Job.assigned_to_id')
    created_jobs = db.relationship('Job', backref='created_by', lazy='dynamic', foreign_keys='Job.created_by_id')

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='client', lazy='dynamic')

    def __repr__(self):
        return f'<Client {self.name}>'

class JobImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id', name='fk_job_image_job_id'), nullable=False)

    def __repr__(self):
        return f'<JobImage {self.filename}>'

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Schedule information
    scheduled_date = db.Column(db.Date)
    scheduled_time = db.Column(db.Time)
    estimated_duration = db.Column(db.Float)  # in hours
    
    # Client information
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', name='fk_job_client_id'))
    location = db.Column(db.String(255))
    
    # Job details
    priority = db.Column(db.String(20))
    materials_needed = db.Column(db.Text)
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    
    # Relationships
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_job_assigned_to_id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_job_created_by_id'))
    images = db.relationship('JobImage', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    
    # Additional fields
    notes = db.Column(db.Text)
    completion_notes = db.Column(db.Text)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Job {self.title}>'

    def update_status(self, new_status):
        self.status = new_status
        if new_status == 'completed' and not self.completed_at:
            self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def get_monthly_stats(year=None, month=None):
        if not year:
            year = datetime.utcnow().year
        query = Job.query.filter(
            db.extract('year', Job.completed_at) == year
        )
        if month:
            query = query.filter(db.extract('month', Job.completed_at) == month)
        
        return query.all()

    @staticmethod
    def search(query_text):
        return Job.query.filter(
            db.or_(
                Job.title.ilike(f'%{query_text}%'),
                Job.description.ilike(f'%{query_text}%'),
                Job.notes.ilike(f'%{query_text}%'),
                Job.location.ilike(f'%{query_text}%'),
                Job.materials_needed.ilike(f'%{query_text}%'),
                db.cast(Job.id, db.String).ilike(f'%{query_text}%')
            )
        ).order_by(Job.created_at.desc()).all()

    @staticmethod
    def get_sorted_jobs(sort_by='created_at', order='desc', search_query=None, status=None):
        query = Job.query

        if search_query:
            query = query.filter(
                db.or_(
                    Job.title.ilike(f'%{search_query}%'),
                    Job.description.ilike(f'%{search_query}%'),
                    Job.notes.ilike(f'%{search_query}%'),
                    Job.location.ilike(f'%{search_query}%'),
                    Job.materials_needed.ilike(f'%{search_query}%'),
                    db.cast(Job.id, db.String).ilike(f'%{search_query}%')
                )
            )

        if status:
            query = query.filter(Job.status == status)

        if sort_by == 'created_at':
            query = query.order_by(Job.created_at.desc() if order == 'desc' else Job.created_at)
        elif sort_by == 'scheduled_date':
            query = query.order_by(Job.scheduled_date.desc() if order == 'desc' else Job.scheduled_date)
        elif sort_by == 'priority':
            query = query.order_by(Job.priority.desc() if order == 'desc' else Job.priority)
        elif sort_by == 'status':
            query = query.order_by(Job.status.desc() if order == 'desc' else Job.status)
        elif sort_by == 'estimated_cost':
            query = query.order_by(Job.estimated_cost.desc() if order == 'desc' else Job.estimated_cost)

        return query

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caller_name = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    reason_for_call = db.Column(db.Text, nullable=False)
    follow_up_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_contact_created_by_id'))
    created_by = db.relationship('User', backref=db.backref('contacts_created', lazy='dynamic'))
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, no_action_needed

    @staticmethod
    def search(query_text):
        return Contact.query.filter(
            db.or_(
                Contact.caller_name.ilike(f'%{query_text}%'),
                Contact.company_name.ilike(f'%{query_text}%'),
                Contact.email.ilike(f'%{query_text}%'),
                Contact.reason_for_call.ilike(f'%{query_text}%'),
                Contact.follow_up_details.ilike(f'%{query_text}%')
            )
        ).order_by(Contact.created_at.desc()).all() 