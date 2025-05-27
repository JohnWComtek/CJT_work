from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User
from routes.clients import clients_bp
from routes.analytics import analytics_bp
from routes.exports import exports_bp
from routes.contacts import contacts_bp
import calendar

login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register custom filters
    @app.template_filter('month_name')
    def month_name_filter(month_number):
        try:
            return calendar.month_name[int(month_number)]
        except (ValueError, IndexError):
            return str(month_number)

    from models import User
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.admin import admin_bp
    from routes.jobs import jobs_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(contacts_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

def create_default_users():
    from models import User, Role
    from werkzeug.security import generate_password_hash

    # Create roles if they don't exist
    roles = {
        'admin': 'Administrator',
        'sales': 'Sales Representative',
        'bookkeeping': 'Bookkeeper',
        'technician': 'Technician',
        'project_manager': 'Project Manager',
        'front_office': 'Front Office'
    }

    for role_name, role_description in roles.items():
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=role_description)
            db.session.add(role)

    # Create default users if they don't exist
    default_users = [
        {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'name': 'Administrator'},
        {'username': 'sales', 'password': 'sales123', 'role': 'sales', 'name': 'Sales Team'},
        {'username': 'bookkeeper', 'password': 'book123', 'role': 'bookkeeping', 'name': 'Bookkeeper'},
        {'username': 'tech1', 'password': 'tech123', 'role': 'technician', 'name': 'Technician 1'},
        {'username': 'tech2', 'password': 'tech123', 'role': 'technician', 'name': 'Technician 2'},
        {'username': 'tech3', 'password': 'tech123', 'role': 'technician', 'name': 'Technician 3'},
        {'username': 'project', 'password': 'project123', 'role': 'project_manager', 'name': 'Project Manager'},
        {'username': 'office', 'password': 'office123', 'role': 'front_office', 'name': 'Front Office'}
    ]

    for user_data in default_users:
        if not User.query.filter_by(username=user_data['username']).first():
            role = Role.query.filter_by(name=user_data['role']).first()
            user = User(
                username=user_data['username'],
                password_hash=generate_password_hash(user_data['password']),
                name=user_data['name']
            )
            user.roles.append(role)
            db.session.add(user)

    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    
    # Create tables and default users within app context
    with app.app_context():
        db.create_all()
        create_default_users()
    
    app.run(debug=True) 