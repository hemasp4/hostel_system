from twilio.rest import Client
from flask import current_app
from ..models.notification import NotificationLog
from .. import db

def send_sms(phone_number, message):
    """Send SMS using Twilio"""
    try:
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        from_phone = current_app.config.get('TWILIO_PHONE')
        
        if not all([account_sid, auth_token, from_phone]):
            return False
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message,
            from_=from_phone,
            to=phone_number
        )
        
        return message.sid is not None
    except Exception as e:
        print(f"SMS Error: {str(e)}")
        return False

def send_leave_sms(phone, status, leave):
    """Send leave status SMS to student"""
    message = f"Your leave request from {leave.start_date} to {leave.end_date} has been {status}."
    
    if status == "approved":
        message += " Please collect your gate pass."
    
    return send_sms(phone, message)

def send_otp_sms(phone, otp):
    """Send OTP for verification"""
    message = f"Your OTP for Hostel Management System is: {otp}. Valid for 5 minutes."
    return send_sms(phone, message)
