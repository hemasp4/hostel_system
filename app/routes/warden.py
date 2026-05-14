from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.leave import LeaveRequest
from app.models.user import User
from app.models.attendance import Attendance
from app.services.leave_service import approve_leave as leave_approve
from app.services.email_service import send_leave_status_email
from app.services.sms_service import send_leave_sms
from app.services.dashboard_service import get_warden_dashboard_data
from app.utils.decorators import role_required
from datetime import datetime, date
from sqlalchemy import func

warden_bp = Blueprint('warden', __name__, url_prefix='/warden')

@warden_bp.route('/dashboard')
@login_required
@role_required('warden')
def dashboard():
    """Warden dashboard"""
    data = get_warden_dashboard_data()
    
    return render_template('warden/dashboard.html',
                         pending_leaves=data['pending_requests'],
                         today_attendance=data['today_scans'],
                         students_on_leave=data['students_on_leave'],
                         weekly_chart=data['weekly_chart'],
                         total_students=User.query.filter_by(role='student').count())

@warden_bp.route('/leave/approve/<int:leave_id>')
@login_required
@role_required('warden')
def approve_leave(leave_id):
    # """Approve leave request"""
    leave = LeaveRequest.query.get_or_404(leave_id)
    
    # if leave.status != 'pending':
    #     flash('This leave request has already been processed', 'warning')
    #     return redirect(url_for('warden.dashboard'))
    
    # # Approve the leave
    success, result = leave_approve(leave_id, current_user.id)
    
    if success:
        # Send notifications
        student = leave.student
        send_leave_status_email(student.email, 'approved', leave)
        if student.phone:
            send_leave_sms(student.phone, 'approved', leave)
        
        flash(f'Leave request approved for {student.name}', 'success')
    else:
        flash(result, 'danger')
    
    return redirect(url_for('warden.dashboard'))

@warden_bp.route('/leave/reject/<int:leave_id>', methods=['GET', 'POST'])
@login_required
@role_required('warden')
def reject_leave(leave_id):
    """Reject leave request"""
    leave = LeaveRequest.query.get_or_404(leave_id)
    
    if leave.status != 'pending':
        flash('This leave request has already been processed', 'warning')
        return redirect(url_for('warden.dashboard'))
    
    # Get rejection reason from form
    remarks = request.form.get('remarks', 'No reason provided')
    
    # Reject the leave
    leave.status = 'rejected'
    leave.approved_by = current_user.id
    leave.approved_at = datetime.utcnow()
    leave.remarks = remarks
    
    db.session.commit()
    
    # Send notifications
    student = leave.student
    send_leave_status_email(student.email, 'rejected', leave)
    if student.phone:
        send_leave_sms(student.phone, 'rejected', leave)
    
    flash(f'Leave request rejected for {student.name}', 'warning')
    return redirect(url_for('warden.dashboard'))

@warden_bp.route('/leave-approvals')
@login_required
@role_required('warden')
def leave_approvals():
    """View all leave requests"""
    # Get pending leaves
    pending_leaves = LeaveRequest.query.filter_by(status='pending')\
                                      .order_by(LeaveRequest.requested_at.desc()).all()
    
    # Get recent actions (last 20)
    recent_actions = LeaveRequest.query.filter(
        LeaveRequest.status.in_(['approved', 'rejected']),
        LeaveRequest.approved_by == current_user.id
    ).order_by(LeaveRequest.approved_at.desc()).limit(20).all()
    
    return render_template('warden/leave_approvals.html',
                         pending_leaves=pending_leaves,
                         recent_actions=recent_actions)

@warden_bp.route('/attendance')
@login_required
@role_required('warden')
def attendance():
    """View attendance records"""
    # Get query parameters
    date_filter = request.args.get('date', '')
    scan_type = request.args.get('type', '')
    student_name = request.args.get('student', '')
    page = request.args.get('page', 1, type=int)
    
    # Build query
    query = Attendance.query.join(User, Attendance.student_id == User.id)
    
    if date_filter:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        query = query.filter(func.date(Attendance.timestamp) == filter_date)
    else:
        # Default to today
        query = query.filter(func.date(Attendance.timestamp) == date.today())
    
    if scan_type:
        query = query.filter(Attendance.scan_type == scan_type)
    
    if student_name:
        query = query.filter(User.name.ilike(f'%{student_name}%'))
    
    # Order by most recent
    query = query.order_by(Attendance.timestamp.desc())
    
    # Paginate
    records = query.paginate(page=page, per_page=20, error_out=False)
    
    # Get statistics
    today = date.today()
    today_exits = Attendance.query.filter(
        func.date(Attendance.timestamp) == today,
        Attendance.scan_type == 'exit'
    ).count()
    
    today_entries = Attendance.query.filter(
        func.date(Attendance.timestamp) == today,
        Attendance.scan_type == 'entry'
    ).count()
    
    # Students currently out
    exits = db.session.query(Attendance.student_id).filter(
        Attendance.scan_type == 'exit',
        func.date(Attendance.timestamp) == today
    ).subquery()
    
    entries = db.session.query(Attendance.student_id).filter(
        Attendance.scan_type == 'entry',
        func.date(Attendance.timestamp) == today
    ).subquery()
    
    currently_out = db.session.query(func.count(exits.c.student_id)).filter(
        ~exits.c.student_id.in_(entries)
    ).scalar() or 0
    
    # Students on leave today
    on_leave_today = LeaveRequest.query.filter(
        LeaveRequest.status == 'approved',
        LeaveRequest.start_date <= today,
        LeaveRequest.end_date >= today
    ).count()
    
    return render_template('warden/attendance.html',
                         records=records,
                         today_exits=today_exits,
                         today_entries=today_entries,
                         currently_out=currently_out,
                         on_leave_today=on_leave_today)

@warden_bp.route('/qr-scanner')
@login_required
@role_required('warden')
def qr_scanner():
    """QR code scanner page"""
    return render_template('warden/qr_scanner.html')

@warden_bp.route('/students')
@login_required
@role_required('warden')
def students_list():
    """View all students"""
    students = User.query.filter_by(role='student', is_active=True)\
                        .order_by(User.name).all()
    
    # Get leave statistics for each student
    student_stats = []
    for student in students:
        total_leaves = student.leaves.count()
        active_leave = student.leaves.filter(
            LeaveRequest.status == 'approved',
            LeaveRequest.start_date <= date.today(),
            LeaveRequest.end_date >= date.today()
        ).first()
        
        student_stats.append({
            'student': student,
            'total_leaves': total_leaves,
            'active_leave': active_leave
        })
    
    return render_template('warden/student_list.html', student_stats=student_stats)

# Add this to app/routes/warden.py

@warden_bp.route('/student/<int:student_id>/details')
@login_required
@role_required('warden')
def student_details(student_id):
    """Get student details (AJAX endpoint)"""
    student = User.query.get_or_404(student_id)
    
    if student.role != 'student':
        return jsonify({'error': 'Not a student'}), 400
    
    # Get leave statistics
    total_leaves = student.leaves.count()
    approved_leaves = student.leaves.filter_by(status='approved').count()
    rejected_leaves = student.leaves.filter_by(status='rejected').count()
    pending_leaves = student.leaves.filter_by(status='pending').count()
    
    return jsonify({
        'id': student.id,
        'name': student.name,
        'email': student.email,
        'phone': student.phone,
        'room_no': getattr(student, 'room_no', None),
        'total_leaves': total_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'pending_leaves': pending_leaves,
        'created_at': student.created_at.strftime('%Y-%m-%d')
    })

@warden_bp.route('/student/<int:student_id>/leaves')
@login_required
@role_required('warden')
def student_leaves(student_id):
    """View specific student's leave history"""
    student = User.query.get_or_404(student_id)
    
    if student.role != 'student':
        flash('Invalid student', 'danger')
        return redirect(url_for('warden.students_list'))
    
    leaves = student.leaves.order_by(LeaveRequest.requested_at.desc()).all()
    
    return render_template('warden/student_leaves.html', 
                         student=student, 
                         leaves=leaves)


@warden_bp.route('/student-status')
@login_required
@role_required(['warden', 'admin'])
def student_status():
    """View current status of all students (in hostel/on leave)"""
    from datetime import date
    today = date.today()
    
    # Get all active students
    all_students = User.query.filter_by(role='student', is_active=True).all()
    
    student_statuses = []
    
    for student in all_students:
        # Check if student has approved leave for today
        active_leave = LeaveRequest.query.filter(
            LeaveRequest.student_id == student.id,
            LeaveRequest.status == 'approved',
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today
        ).first()
        
        # Check today's attendance (last scan)
        last_scan = Attendance.query.filter_by(
            student_id=student.id
        ).filter(
            func.date(Attendance.timestamp) == today
        ).order_by(Attendance.timestamp.desc()).first()
        
        # Determine status
        if active_leave:
            if last_scan:
                # Student on leave but has scan record
                if last_scan.scan_type == 'exit':
                    status = 'on_leave_outside'  # Left the hostel
                else:
                    status = 'on_leave_inside'   # Returned to hostel
            else:
                status = 'on_leave_no_scan'      # No scan record today
        else:
            # No active leave
            if last_scan and last_scan.scan_type == 'exit':
                status = 'outside_no_leave'      # Outside without leave
            else:
                status = 'inside'                # Present in hostel
        
        student_statuses.append({
            'student': student,
            'active_leave': active_leave,
            'last_scan': last_scan,
            'status': status
        })
    
    # Count statistics
    stats = {
        'total_students': len(all_students),
        'present_in_hostel': len([s for s in student_statuses if s['status'] in ['inside', 'on_leave_inside']]),
        'on_approved_leave': len([s for s in student_statuses if s['active_leave'] is not None]),
        'outside_hostel': len([s for s in student_statuses if s['status'] in ['on_leave_outside', 'outside_no_leave']]),
        'outside_without_leave': len([s for s in student_statuses if s['status'] == 'outside_no_leave'])
    }
    
    return render_template('warden/student_status.html', 
                         student_statuses=student_statuses,
                         stats=stats,
                         today=today)

