from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import User, Role, db
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('admin'):
            flash('You need to be an administrator to access this page.')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def index():
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/index.html', users=users, roles=roles)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users/index.html', users=users)

@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.name = request.form['name']
        
        if request.form.get('password'):
            user.password_hash = generate_password_hash(request.form['password'])
            
        # Update roles
        user.roles = []
        for role in roles:
            if request.form.get(f'role_{role.id}'):
                user.roles.append(role)
                
        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('admin.list_users'))
        
    return render_template('admin/users/edit.html', user=user, roles=roles)

@admin_bp.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    roles = Role.query.all()
    
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            name=request.form['name'],
            password_hash=generate_password_hash(request.form['password'])
        )
        
        for role in roles:
            if request.form.get(f'role_{role.id}'):
                user.roles.append(role)
                
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!')
        return redirect(url_for('admin.list_users'))
        
    return render_template('admin/users/new.html', roles=roles) 