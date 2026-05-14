# This file makes the routes directory a Python package
# Import all blueprints here for easy access

from .auth import auth_bp
from .main import main_bp
from .student import student_bp
from .warden import warden_bp
from .admin import admin_bp
from .leave import leave_bp
from .qr import qr_bp

__all__ = [
    'auth_bp',
    'main_bp',
    'student_bp',
    'warden_bp',
    'admin_bp',
    'leave_bp',
    'qr_bp'
]
