from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from ..models.user import User

def generate_reset_token(email):
    """Generate password reset token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    """Verify password reset token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return User.query.filter_by(email=email).first()
    except:
        return None
