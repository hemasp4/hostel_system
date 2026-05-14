from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(roles):
    """Decorator to check if user has required role(s)"""
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.role != 'admin' and current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.landing'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
