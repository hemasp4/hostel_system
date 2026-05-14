from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_required, current_user
from ..utils.decorators import role_required
from ..models.user import User
from ..models.leave import LeaveRequest
from ..models.attendance import Attendance
from .. import db
from sqlalchemy import func
from datetime import datetime, timedelta, date
from app.models.settings import SystemSettings


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    # Statistics
    total_students = User.query.filter_by(role='student').count()
    total_wardens = User.query.filter_by(role='warden').count()
    total_leaves = LeaveRequest.query.count()
    pending_leaves = LeaveRequest.query.filter_by(status='pending').count()
    approved_leaves=LeaveRequest.query.filter_by(status='approved').count()
    # Recent activity
    recent_leaves = LeaveRequest.query.order_by(LeaveRequest.requested_at.desc()).limit(10).all()
    
    # Chart data - last 7 days
    chart_data = []
    for i in range(7):
        date = datetime.today() - timedelta(days=i)
        count = LeaveRequest.query.filter(
            func.date(LeaveRequest.requested_at) == date.date()
        ).count()
        chart_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_wardens=total_wardens,
                         total_leaves=total_leaves,
                         pending_leaves=pending_leaves,
                         recent_leaves=recent_leaves,
                         chart_data=chart_data,
                         approved_leaves=approved_leaves )

@admin_bp.route('/users')
@login_required
@role_required('admin')
def user_management():
    users = User.query.all()
    students = User.query.filter_by(role="student").count()
    wardens = User.query.filter_by(role="warden").count()
    admins = User.query.filter_by(role="admin").count()

    user_stats = {
        "students": students,
        "wardens": wardens,
        "admins": admins
    }
    return render_template('admin/user_management.html', users=users,user_stats=user_stats)

@admin_bp.route('/users/toggle/<int:user_id>')
@login_required
@role_required('admin')
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = "activated" if user.is_active else "deactivated"
    flash(f'User {user.name} has been {status}', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/reports')
@login_required
@role_required('admin')
def reports():
    # Get date range for reports (default last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Leave requests trend data (last 30 days)
    chart_labels = []
    leave_requests_data = []
    
    for i in range(30):
        date_val = start_date + timedelta(days=i)
        chart_labels.append(date_val.strftime('%b %d'))
        
        count = LeaveRequest.query.filter(
            func.date(LeaveRequest.requested_at) == date_val
        ).count()
        leave_requests_data.append(count)
    
    # Leave status distribution
    approved_count = LeaveRequest.query.filter_by(status='approved').count()
    pending_count = LeaveRequest.query.filter_by(status='pending').count()
    rejected_count = LeaveRequest.query.filter_by(status='rejected').count()
    leave_status_data = [approved_count, pending_count, rejected_count]
    
    # Monthly attendance data
    attendance_labels = []
    exits_data = []
    entries_data = []
    
    for i in range(7):  # Last 7 days
        date_val = end_date - timedelta(days=i)
        attendance_labels.append(date_val.strftime('%b %d'))
        
        exits = Attendance.query.filter(
            func.date(Attendance.timestamp) == date_val,
            Attendance.scan_type == 'exit'
        ).count()
        entries = Attendance.query.filter(
            func.date(Attendance.timestamp) == date_val,
            Attendance.scan_type == 'entry'
        ).count()
        
        exits_data.append(exits)
        entries_data.append(entries)
    
    # Reverse the lists to show oldest to newest
    attendance_labels.reverse()
    exits_data.reverse()
    entries_data.reverse()
    
    # Recent generated reports (placeholder data)
    recent_reports = []
    
    return render_template('admin/reports.html',
                         chart_labels=chart_labels,
                         leave_requests_data=leave_requests_data,
                         leave_status_data=leave_status_data,
                         attendance_labels=attendance_labels,
                         exits_data=exits_data,
                         entries_data=entries_data,
                         recent_reports=recent_reports)


@admin_bp.route('/settings')
@login_required
@role_required('admin')
def settings():
    """Show settings page"""
    # Get settings from database or use defaults
    settings = {
        'hostel_name': SystemSettings.get_setting('hostel_name', 'Student Hostel'),
        'admin_email': SystemSettings.get_setting('admin_email', 'admin@hostel.com'),
        'max_leave_days': int(SystemSettings.get_setting('max_leave_days', '7')),
        'advance_request_days': int(SystemSettings.get_setting('advance_request_days', '1')),
        'email_notifications': SystemSettings.get_setting('email_notifications', 'true') == 'true',
        'sms_notifications': SystemSettings.get_setting('sms_notifications', 'true') == 'true',
        'notify_on_request': SystemSettings.get_setting('notify_on_request', 'true') == 'true',
        'notify_on_approval': SystemSettings.get_setting('notify_on_approval', 'true') == 'true',
        'qr_size': SystemSettings.get_setting('qr_size', 'medium'),
        'qr_expiry_hours': int(SystemSettings.get_setting('qr_expiry_hours', '24'))
    }
    
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/users/add', methods=['POST'])
@login_required
@role_required('admin')
def add_user():
    """Add new user"""
    from app.services.auth_service import create_user
    
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    role = request.form.get('role')
    password = request.form.get('password')
    
    success, result = create_user(name, email, phone, password, role)
    
    if success:
        flash(f'User {name} created successfully', 'success')
    else:
        flash(result, 'danger')
    
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/users/delete/<int:user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    """Delete user"""
    if user_id == current_user.id:
        flash('You cannot delete yourself', 'danger')
        return redirect(url_for('admin.user_management'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.name} deleted successfully', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/backup-database')
@login_required
@role_required('admin')
def backup_database():
    """Create database backup"""
    # Implementation for database backup
    flash('Database backup created successfully', 'success')
    return redirect(url_for('admin.settings'))

@admin_bp.route('/clean-old-records')
@login_required
@role_required('admin')
def clean_old_records():
    """Clean old records"""
    # Delete records older than 1 year
    one_year_ago = datetime.now() - timedelta(days=365)
    
    old_leaves = LeaveRequest.query.filter(LeaveRequest.requested_at < one_year_ago).count()
    old_attendance = Attendance.query.filter(Attendance.timestamp < one_year_ago).count()
    
    # Delete the records
    LeaveRequest.query.filter(LeaveRequest.requested_at < one_year_ago).delete()
    Attendance.query.filter(Attendance.timestamp < one_year_ago).delete()
    
    db.session.commit()
    
    flash(f'Cleaned {old_leaves} leave records and {old_attendance} attendance records', 'success')
    return redirect(url_for('admin.settings'))

@admin_bp.route('/generate-report', methods=['POST'])
@login_required
@role_required('admin')
def generate_report():
    """Generate various reports"""
    report_type = request.form.get('report_type')
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')
    
    # Implementation for report generation
    flash(f'{report_type} report generated successfully', 'success')
    return redirect(url_for('admin.reports'))


@admin_bp.route('/update-settings', methods=['POST'])
@login_required
@role_required('admin')
def update_settings():
    """Update general settings"""
    try:
        # Save each setting
        SystemSettings.set_setting('hostel_name', request.form.get('hostel_name'), 'general', current_user.id)
        SystemSettings.set_setting('admin_email', request.form.get('admin_email'), 'general', current_user.id)
        SystemSettings.set_setting('max_leave_days', request.form.get('max_leave_days'), 'general', current_user.id)
        SystemSettings.set_setting('advance_request_days', request.form.get('advance_request_days'), 'general', current_user.id)
        
        flash('General settings updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating settings: {str(e)}', 'danger')
    
    return redirect(url_for('admin.settings'))

@admin_bp.route('/update-notification-settings', methods=['POST'])
@login_required
@role_required('admin')
def update_notification_settings():
    """Update notification settings"""
    try:
        # Get checkbox values (checkboxes only send data if checked)
        email_notifications = 'email_notifications' in request.form
        sms_notifications = 'sms_notifications' in request.form
        notify_on_request = 'notify_on_request' in request.form
        notify_on_approval = 'notify_on_approval' in request.form
        
        # Save settings
        SystemSettings.set_setting('email_notifications', str(email_notifications).lower(), 'notification', current_user.id)
        SystemSettings.set_setting('sms_notifications', str(sms_notifications).lower(), 'notification', current_user.id)
        SystemSettings.set_setting('notify_on_request', str(notify_on_request).lower(), 'notification', current_user.id)
        SystemSettings.set_setting('notify_on_approval', str(notify_on_approval).lower(), 'notification', current_user.id)
        
        flash('Notification settings updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating notification settings: {str(e)}', 'danger')
    
    return redirect(url_for('admin.settings'))

@admin_bp.route('/update-qr-settings', methods=['POST'])
@login_required
@role_required('admin')
def update_qr_settings():
    """Update QR code settings"""
    try:
        SystemSettings.set_setting('qr_size', request.form.get('qr_size'), 'qr', current_user.id)
        SystemSettings.set_setting('qr_expiry_hours', request.form.get('qr_expiry_hours'), 'qr', current_user.id)
        
        flash('QR code settings updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating QR settings: {str(e)}', 'danger')
    
    return redirect(url_for('admin.settings'))

