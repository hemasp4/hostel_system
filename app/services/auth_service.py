from ..models.user import User
from ..models.notification import NotificationLog
from .. import db
from .email_service import send_welcome_email, send_password_reset_email
from ..utils.token_utils import generate_reset_token

def create_user(name, email, phone, password, role='student'):
    """Create new user with validation"""
    email = email.lower().strip()
    if User.query.filter_by(email=email).first():
        return False, "Email already registered"
    
    user = User(
        name=name,
        email=email.lower().strip(),
        phone=phone,
        role=role
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        send_welcome_email(email, name)
        
        return True, user
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def initiate_password_reset(email):
    """Initiate password reset process"""
    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user:
        return False, "Email not found"
    
    token = generate_reset_token(email)
    reset_link = f"http://localhost:5000/auth/reset_password/{token}"
    
    send_password_reset_email(email, user.name, reset_link)
    
    notification = NotificationLog(
        user_id=user.id,
        type='email',
        recipient=email,  
        subject='Password Reset Request',  
        message=f'Password reset link sent to {email}',
        status='sent'
    )
    db.session.add(notification)
    
    try:
        db.session.commit()
        return True, "Password reset email sent"
    except Exception as e:
        db.session.rollback()
        return False, f"Error sending reset email: {str(e)}"
