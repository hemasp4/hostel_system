from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)  # Initialize Flask-Mail
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Import models to ensure they are registered with SQLAlchemy
    from app.models import user, leave, attendance, notification

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.warden import warden_bp
    from app.routes.admin import admin_bp
    from app.routes.leave import leave_bp
    from app.routes.qr import qr_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(warden_bp, url_prefix='/warden')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(leave_bp, url_prefix='/leave')
    app.register_blueprint(qr_bp, url_prefix='/qr')

    # Create database tables
    with app.app_context():
        db.create_all()
        # Add profile_image column if not exists
        try:
            from sqlalchemy import text
            db.session.execute(text('ALTER TABLE users ADD COLUMN profile_image VARCHAR(255)'))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # Context processor to inject pending leave count globally for the sidebar badge
    @app.context_processor
    def inject_pending_leaves_count():
        from app.models.leave import LeaveRequest
        try:
            count = LeaveRequest.query.filter_by(status='pending').count()
        except Exception:
            count = 0
        return dict(pending_leaves_count=count)

    return app
