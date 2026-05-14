import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Email Configuration Debug ===")
print(f"MAIL_SERVER: {os.getenv('MAIL_SERVER')}")
print(f"MAIL_PORT: {os.getenv('MAIL_PORT')}")
print(f"MAIL_USE_TLS: {os.getenv('MAIL_USE_TLS')}")
print(f"MAIL_USE_SSL: {os.getenv('MAIL_USE_SSL')}")
print(f"MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
print(f"MAIL_PASSWORD: {'*' * len(os.getenv('MAIL_PASSWORD', '')) if os.getenv('MAIL_PASSWORD') else 'NOT SET'}")
print(f"MAIL_DEFAULT_SENDER: {os.getenv('MAIL_DEFAULT_SENDER')}")

# Test with direct SMTP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("\n=== Testing Direct SMTP Connection ===")

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = os.getenv('MAIL_USERNAME')
    msg['To'] = os.getenv('MAIL_USERNAME')  # Send to yourself
    msg['Subject'] = "Test Email from Hostel Management System"
    
    body = "This is a test email to verify SMTP configuration."
    msg.attach(MIMEText(body, 'plain'))
    
    # Connect to server
    print("Connecting to Gmail SMTP server...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print("TLS started successfully")
    
    # Login
    print("Attempting to login...")
    server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
    print("Login successful!")
    
    # Send email
    print("Sending email...")
    text = msg.as_string()
    server.sendmail(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_USERNAME'), text)
    server.quit()
    print("Email sent successfully!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

# Test with Flask app
print("\n=== Testing with Flask App ===")
from app import create_app
from app.services.email_service import send_password_reset_email

app = create_app()

with app.app_context():
    try:
        # Print Flask config
        print(f"Flask MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"Flask MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"Flask MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"Flask MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        
        # Try sending email
        result = send_password_reset_email(
            os.getenv('MAIL_USERNAME'),  # Send to yourself
            "Test User",
            "http://localhost:5000/test-link"
        )
        print(f"Email send result: {result}")
    except Exception as e:
        print(f"Flask Error: {str(e)}")
        import traceback
        traceback.print_exc()
