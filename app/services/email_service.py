import os
import requests
from flask import current_app
from flask_mail import Message
from app import mail, db
from ..models.notification import NotificationLog

def send_email_via_gmail(to_email, subject, html_content):
    """Send email using Gmail with App Password"""
    try:
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[to_email]
        )
        msg.html = html_content
        
        # Also add plain text version
        msg.body = html_content.replace('<br>', '\n').replace('</p>', '\n').replace('<[^<]+?>', '')
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_email_via_resend(to_email, subject, html_content):
    """Send email using Resend API (fallback)"""
    api_key = current_app.config.get('RESEND_API_KEY')
    
    if not api_key:
        return False
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@yourhostel.com'),
                "to": to_email,
                "subject": subject,
                "html": html_content
            }
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending email via Resend: {str(e)}")
        return False

def send_email(to_email, subject, html_content):
    """Send email using Gmail first, fallback to Resend if needed"""
    # Try Gmail first
    if current_app.config.get('MAIL_USERNAME') and current_app.config.get('MAIL_PASSWORD'):
        if send_email_via_gmail(to_email, subject, html_content):
            return True
    
    # Fallback to Resend if Gmail fails
    if current_app.config.get('RESEND_API_KEY'):
        return send_email_via_resend(to_email, subject, html_content)
    
    return False

def send_welcome_email(email, name):
    """Send welcome email to new user"""
    subject = "Welcome to Hostel Management System"
    html = f"""
    <html>
    <body>
        <h2>Welcome {name}!</h2>
        <p>Your account has been successfully created.</p>
        <p>You can now login and submit leave requests.</p>
        <br>
        <p>Best regards,<br>Hostel Management Team</p>
    </body>
    </html>
    """
    
    return send_email(email, subject, html)

def send_password_reset_email(email, name, reset_link):
    """Send password reset email using Gmail"""
    subject = "Password Reset Request - Hostel Management System"
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2196F3;">Password Reset Request</h2>
            <p>Hello {name},</p>
            <p>You requested a password reset for your Hostel Management System account.</p>
            <p>Click the button below to reset your password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background-color: #2196F3; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </div>
            <p style="color: #666; font-size: 14px;">Or copy and paste this link in your browser:</p>
            <p style="color: #2196F3; word-break: break-all;">{reset_link}</p>
            <hr style="border: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 14px;">
                This link will expire in 1 hour for security reasons.
            </p>
            <p style="color: #666; font-size: 14px;">
                If you didn't request this password reset, please ignore this email.
                Your password will remain unchanged.
            </p>
            <br>
            <p>Best regards,<br>
            <strong>Hostel Management Team</strong></p>
        </div>
    </body>
    </html>
    """
    
    return send_email(email, subject, html)

def send_leave_request_email(warden_email, student_name, leave):
    """Notify warden of new leave request"""
    subject = f"New Leave Request from {student_name}"
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4CAF50;">New Leave Request</h2>
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px;">
                <p><strong>Student:</strong> {student_name}</p>
                <p><strong>Reason:</strong> {leave.reason}</p>
                <p><strong>Duration:</strong> {leave.start_date.strftime('%B %d, %Y')} to {leave.end_date.strftime('%B %d, %Y')}</p>
                <p><strong>Number of Days:</strong> {(leave.end_date - leave.start_date).days + 1}</p>
            </div>
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:5000/warden/dashboard" 
                   style="background-color: #4CAF50; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Review Request
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(warden_email, subject, html)

def send_leave_status_email(student_email, status, leave):
    """Notify student of leave status update"""
    subject = f"Leave Request {status.capitalize()}"
    color = "#4CAF50" if status == "approved" else "#f44336"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: {color};">Leave Request {status.capitalize()}</h2>
            <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px;">
                <p>Your leave request has been <strong style="color: {color};">{status}</strong>.</p>
                <p><strong>Duration:</strong> {leave.start_date.strftime('%B %d, %Y')} to {leave.end_date.strftime('%B %d, %Y')}</p>
                <p><strong>Reason:</strong> {leave.reason}</p>
            </div>
    """
    
    if status == "approved" and leave.qr_code:
        html += f"""
            <div style="text-align: center; margin: 30px 0;">
                <h3>Your QR Code</h3>
                <p>Please show this QR code at the gate:</p>
                <img src="{leave.qr_code}" alt="QR Code" style="max-width: 300px; border: 1px solid #ddd; padding: 10px;">
            </div>
        """
    
    if status == "rejected" and leave.remarks:
        html += f"""
            <div style="margin-top: 20px;">
                <p><strong>Remarks:</strong> {leave.remarks}</p>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return send_email(student_email, subject, html)

# Test function to verify email configuration
def test_email_configuration():
    """Test if email configuration is working"""
    try:
        test_email = current_app.config.get('MAIL_USERNAME')
        if not test_email:
            return False, "Email not configured"
        
        subject = "Test Email - Hostel Management System"
        html = """
        <html>
        <body>
            <h2>Test Email</h2>
            <p>This is a test email to verify your email configuration is working correctly.</p>
            <p>If you received this email, your Gmail App Password is configured properly!</p>
        </body>
        </html>
        """
        
        if send_email(test_email, subject, html):
            return True, "Test email sent successfully"
        else:
            return False, "Failed to send test email"
    except Exception as e:
        return False, f"Error: {str(e)}"
