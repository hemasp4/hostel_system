from datetime import datetime, timedelta

def format_date(date):
    """Format date to readable string"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    return date.strftime('%B %d, %Y')

def format_datetime(dt):
    """Format datetime to readable string"""
    return dt.strftime('%B %d, %Y at %I:%M %p')

def days_between(start_date, end_date):
    """Calculate days between two dates"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    return (end_date - start_date).days + 1

def is_past_date(date):
    """Check if date is in the past"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    return date < datetime.today().date()
