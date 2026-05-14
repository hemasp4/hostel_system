from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models.user import User
from app.models.leave import LeaveRequest
from app.models.attendance import Attendance
from sqlalchemy import func
from datetime import datetime, date

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to landing page"""
    return redirect(url_for('main.landing'))

@main_bp.route('/home')
def landing():
    """Landing page with statistics and features"""
    # Get statistics for landing page
    stats = {
        'total_students': 0,
        'total_staff': 0,
        'total_leaves': 0,
        'active_leaves': 0
    }
    
    if current_user.is_authenticated:
        # Get real statistics
        stats['total_students'] = User.query.filter_by(role='student', is_active=True).count()
        stats['total_staff'] = User.query.filter(
            User.role.in_(['warden', 'admin']),
            User.is_active == True
        ).count()
        stats['total_leaves'] = LeaveRequest.query.count()
        stats['active_leaves'] = LeaveRequest.query.filter(
            LeaveRequest.status == 'approved',
            LeaveRequest.start_date <= date.today(),
            LeaveRequest.end_date >= date.today()
        ).count()
    else:
        # Show demo statistics for non-authenticated users
        stats = {
            'total_students': 500,
            'total_staff': 50,
            'total_leaves': 1000,
            'active_leaves': 24
        }
    
    return render_template('landing.html', stats=stats)

@main_bp.route('/dashboard')
def dashboard():
    """Redirect to role-specific dashboard"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Redirect based on user role
    if current_user.role == 'student':
        return redirect(url_for('student.dashboard'))
    elif current_user.role == 'warden':
        return redirect(url_for('warden.dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        # Default fallback
        return redirect(url_for('main.landing'))

@main_bp.route('/about')
def about():
    """About page"""
    features = [
        {
            'icon': 'fas fa-calendar-check',
            'title': 'Leave Management',
            'description': 'Easy leave request submission and approval workflow'
        },
        {
            'icon': 'fas fa-qrcode',
            'title': 'QR Code System',
            'description': 'Secure QR codes for gate pass verification'
        },
        {
            'icon': 'fas fa-bell',
            'title': 'Instant Notifications',
            'description': 'Email and SMS alerts for important updates'
        },
        {
            'icon': 'fas fa-chart-line',
            'title': 'Analytics Dashboard',
            'description': 'Real-time statistics and reporting'
        },
        {
            'icon': 'fas fa-shield-alt',
            'title': 'Secure Access',
            'description': 'Role-based access control for data security'
        },
        {
            'icon': 'fas fa-mobile-alt',
            'title': 'Mobile Friendly',
            'description': 'Responsive design works on all devices'
        }
    ]
    
    return render_template('about.html', features=features)

@main_bp.route('/contact')
def contact():
    """Contact page"""
    contact_info = {
        'email': 'admin@hostel.com',
        'phone': '+1234567890',
        'address': 'Student Hostel, University Campus',
        'hours': 'Monday - Friday: 9:00 AM - 5:00 PM'
    }
    
    return render_template('contact.html', contact_info=contact_info)

@main_bp.route('/features')
def features():
    """Features page"""
    feature_list = {
        'student': [
            'Submit leave requests online',
            'Track leave request status',
            'Download approved leave pass',
            'View leave history',
            'Update profile information',
            'Receive email/SMS notifications'
        ],
        'warden': [
            'Review and approve leave requests',
            'Scan QR codes at gate',
            'View attendance records',
            'Monitor student movements',
            'Generate reports',
            'Send notifications to students'
        ],
        'admin': [
            'Manage all users',
            'View comprehensive analytics',
            'Configure system settings',
            'Generate detailed reports',
            'Monitor system activity',
            'Backup and restore data'
        ]
    }
    
    return render_template('features.html', features=feature_list)

@main_bp.route('/help')
def help():
    """Help/FAQ page"""
    faqs = [
        {
            'question': 'How do I request leave?',
            'answer': 'Login to your student account, go to "Request Leave" from the dashboard, fill in the details and submit.'
        },
        {
            'question': 'How long does leave approval take?',
            'answer': 'Leave requests are typically processed within 24 hours. You will receive notification once processed.'
        },
        {
            'question': 'Can I cancel my leave request?',
            'answer': 'Yes, you can cancel pending leave requests from your leave history page.'
        },
        {
            'question': 'What if I lose my QR code?',
            'answer': 'You can regenerate the QR code from your leave history page for any approved leave.'
        },
        {
            'question': 'How do I reset my password?',
            'answer': 'Click on "Forgot Password" on the login page and follow the instructions sent to your email.'
        }
    ]
    
    return render_template('help.html', faqs=faqs)

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

# Error handlers
@main_bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500

@main_bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('errors/403.html'), 403

# Health check endpoint
@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        User.query.first()
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Hostel Management System'
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, 503
