from ..models.user import User
from ..models.leave import LeaveRequest
from ..models.attendance import Attendance
from sqlalchemy import func
from datetime import datetime, timedelta

def get_student_dashboard_data(student_id):
    """Get dashboard data for student"""
    # Recent leaves
    recent_leaves = LeaveRequest.query.filter_by(student_id=student_id)\
                                     .order_by(LeaveRequest.requested_at.desc())\
                                     .limit(5).all()
    
    # Statistics
    stats = {
        'total_leaves': LeaveRequest.query.filter_by(student_id=student_id).count(),
        'approved_leaves': LeaveRequest.query.filter_by(student_id=student_id, status='approved').count(),
        'pending_leaves': LeaveRequest.query.filter_by(student_id=student_id, status='pending').count(),
        'days_out': 0
    }
    
    # Calculate total days out
    approved_leaves = LeaveRequest.query.filter_by(student_id=student_id, status='approved').all()
    for leave in approved_leaves:
        stats['days_out'] += (leave.end_date - leave.start_date).days + 1
    
    return {
        'recent_leaves': recent_leaves,
        'statistics': stats
    }

def get_warden_dashboard_data():
    """Get dashboard data for warden"""
    # Pending requests
    pending_requests = LeaveRequest.query.filter_by(status='pending')\
                                        .order_by(LeaveRequest.requested_at.desc()).all()
    
    # Today's statistics
    today = datetime.today().date()
    today_scans = Attendance.query.filter(
        func.date(Attendance.timestamp) == today
    ).count()
    
    # Students currently on leave
    on_leave = LeaveRequest.query.filter(
        LeaveRequest.status == 'approved',
        LeaveRequest.start_date <= today,
        LeaveRequest.end_date >= today
    ).count()
    
    # Weekly chart data
    weekly_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = LeaveRequest.query.filter(
            func.date(LeaveRequest.requested_at) == date
        ).count()
        weekly_data.append({
            'date': date.strftime('%a'),
            'count': count
        })
    
    return {
        'pending_requests': pending_requests,
        'today_scans': today_scans,
        'students_on_leave': on_leave,
        'weekly_chart': list(reversed(weekly_data))
    }

def get_admin_dashboard_data():
    """Get comprehensive dashboard data for admin"""
    # User statistics
    user_stats = {
        'total_students': User.query.filter_by(role='student').count(),
        'total_wardens': User.query.filter_by(role='warden').count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'inactive_users': User.query.filter_by(is_active=False).count()
    }
    
    # Leave statistics
    leave_stats = {
        'total_requests': LeaveRequest.query.count(),
        'approved': LeaveRequest.query.filter_by(status='approved').count(),
        'pending': LeaveRequest.query.filter_by(status='pending').count(),
        'rejected': LeaveRequest.query.filter_by(status='rejected').count()
    }
    
    # Monthly trend
    monthly_trend = []
    for i in range(12):
        month_start = datetime.today().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = LeaveRequest.query.filter(
            LeaveRequest.requested_at >= month_start,
            LeaveRequest.requested_at <= month_end
        ).count()
        
        monthly_trend.append({
            'month': month_start.strftime('%b'),
            'count': count
        })
    
    return {
        'user_stats': user_stats,
        'leave_stats': leave_stats,
        'monthly_trend': list(reversed(monthly_trend[-6:]))  # Last 6 months
    }
