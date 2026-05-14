# This file makes the services directory a Python package
# Import all services here for easy access

from .auth_service import *
from .leave_service import *
from .qr_service import *
from .email_service import *
from .sms_service import *
from .dashboard_service import *

__all__ = [
    'create_user',
    'initiate_password_reset',
    'create_leave_request',
    'approve_leave',
    'get_leave_statistics',
    'generate_qr_code',
    'validate_qr_code',
    'send_email_via_resend',
    'send_welcome_email',
    'send_leave_request_email',
    'send_leave_status_email',
    'send_sms',
    'send_leave_sms',
    'get_student_dashboard_data',
    'get_warden_dashboard_data',
    'get_admin_dashboard_data'
]
