from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///school_management.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.views.main import main
    from app.views.auth import auth
    from app.views.super_admin import super_admin
    from app.views.admin import admin
    from app.views.teacher import teacher
    from app.views.student import student
    from app.views.parent import parent
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(super_admin)
    app.register_blueprint(admin)
    app.register_blueprint(teacher)
    app.register_blueprint(student)
    app.register_blueprint(parent)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Check if super admin exists, if not create one
        from app.models.user import User, Role
        from app.utils.seeder import create_roles, create_super_admin
        
        create_roles()
        create_super_admin()
    
    return app