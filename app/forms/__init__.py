# This file makes the forms directory a Python package
# Import all forms here for easy access

from .auth_forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from .leave_forms import LeaveRequestForm
from .profile_forms import ProfileUpdateForm

__all__ = [
    'LoginForm',
    'RegisterForm',
    'ForgotPasswordForm',
    'ResetPasswordForm',
    'LeaveRequestForm',
    'ProfileUpdateForm'
]
