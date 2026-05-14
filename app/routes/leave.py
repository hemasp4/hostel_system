from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify,make_response
from flask_login import login_required, current_user
from app import db
from app.models.leave import LeaveRequest
from app.models.user import User
from app.forms.leave_forms import LeaveRequestForm
from app.services.leave_service import create_leave_request
from app.services.email_service import send_leave_request_email
from app.utils.decorators import role_required
from datetime import datetime
try:
    import pdfkit
    # Explicit path for Windows - wkhtmltopdf is not auto-added to PATH
    WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    import os as _os
    PDFKIT_AVAILABLE = _os.path.exists(WKHTMLTOPDF_PATH)
    if PDFKIT_AVAILABLE:
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    else:
        PDFKIT_CONFIG = None
except ImportError:
    PDFKIT_AVAILABLE = False
    PDFKIT_CONFIG = None

leave_bp = Blueprint('leave', __name__, url_prefix='/leave')

@leave_bp.route('/request', methods=['GET', 'POST'])
@login_required
@role_required('student')
def request_leave():
    """Submit new leave request"""
    form = LeaveRequestForm()
    
    if form.validate_on_submit():
        # Create leave request
        success, result = create_leave_request(
            student_id=current_user.id,
            reason=form.reason.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        
        if success:
            flash('Leave request submitted successfully!', 'success')
            
            # Notify wardens
            wardens = User.query.filter_by(role='warden', is_active=True).all()
            for warden in wardens:
                send_leave_request_email(warden.email, current_user.name, result)
            
            return redirect(url_for('student.dashboard'))
        else:
            flash(result, 'danger')
    
    return render_template('student/leave_request.html', form=form)

@leave_bp.route('/history')
@login_required
def history():
    """View leave history"""
    # Get filter parameters
    status = request.args.get('status', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    page = request.args.get('page', 1, type=int)
    
    # Build query
    query = LeaveRequest.query
    
    if current_user.role == 'student':
        query = query.filter_by(student_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    if from_date:
        query = query.filter(LeaveRequest.start_date >= datetime.strptime(from_date, '%Y-%m-%d').date())
    
    if to_date:
        query = query.filter(LeaveRequest.end_date <= datetime.strptime(to_date, '%Y-%m-%d').date())
    
    # Order by most recent first
    query = query.order_by(LeaveRequest.requested_at.desc())
    
    # Paginate results
    leaves = query.paginate(page=page, per_page=10, error_out=False)
    
    return render_template('student/leave_history.html', leaves=leaves)

@leave_bp.route('/details/<int:leave_id>')
@login_required
def leave_details(leave_id):
    """Get leave details (AJAX endpoint)"""
    leave = LeaveRequest.query.get_or_404(leave_id)
    
    # Check permission
    if current_user.role == 'student' and leave.student_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': leave.id,
        'student_name': leave.student.name,
        'student_email': leave.student.email,
        'student_phone': leave.student.phone,
        'reason': leave.reason,
        'start_date': leave.start_date.strftime('%Y-%m-%d'),
        'end_date': leave.end_date.strftime('%Y-%m-%d'),
        'duration': (leave.end_date - leave.start_date).days + 1,
        'status': leave.status,
        'requested_at': leave.requested_at.strftime('%Y-%m-%d %H:%M'),
        'approved_by': leave.approver.name if leave.approver else None,
        'approved_at': leave.approved_at.strftime('%Y-%m-%d %H:%M') if leave.approved_at else None,
        'remarks': leave.remarks,
        'qr_code': leave.qr_code
    })

@leave_bp.route('/cancel/<int:leave_id>', methods=['POST'])
@login_required
@role_required('student')
def cancel_leave(leave_id):
    """Cancel pending leave request"""
    leave = LeaveRequest.query.get_or_404(leave_id)
    
    # Check ownership
    if leave.student_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('leave.history'))
    
    # Check if can be cancelled
    if leave.status != 'pending':
        flash('Only pending leave requests can be cancelled', 'warning')
        return redirect(url_for('leave.history'))
    
    # Cancel the leave
    leave.status = 'cancelled'
    leave.remarks = 'Cancelled by student'
    db.session.commit()
    
    flash('Leave request cancelled successfully', 'success')
    return redirect(url_for('leave.history'))

@leave_bp.route('/print/<int:leave_id>')
@login_required
def print_leave(leave_id):
    """Print leave pass"""
    leave = LeaveRequest.query.get_or_404(leave_id)
    
    # Check permission
    if current_user.role == 'student' and leave.student_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('leave.history'))
    
    # Check if approved
    if leave.status != 'approved':
        flash('Only approved leaves can be printed', 'warning')
        return redirect(url_for('leave.history'))
    
    return render_template('student/leave_print.html', leave=leave)



@leave_bp.route('/download-pdf/<int:leave_id>')
@login_required
def download_pdf(leave_id):
    """Generate and download PDF for leave pass"""
    leave = LeaveRequest.query.get_or_404(leave_id)
    
    # Check permission
    if current_user.role == 'student' and leave.student_id != current_user.id:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('leave.history'))
    
    # Check if pdfkit/wkhtmltopdf is available
    if not PDFKIT_AVAILABLE:
        flash('PDF generation requires wkhtmltopdf. Please install it from https://wkhtmltopdf.org/downloads.html', 'warning')
        return redirect(url_for('leave.print_leave', leave_id=leave_id))

    # Render the template
    html = render_template('student/leave_print.html', leave=leave)

    try:
        # Generate PDF with explicit wkhtmltopdf path (Windows)
        pdf = pdfkit.from_string(html, False, configuration=PDFKIT_CONFIG)

        # Create response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=leave_pass_{leave_id}.pdf'
        return response
    except OSError:
        flash('PDF generation failed: wkhtmltopdf binary not found. Please install it from https://wkhtmltopdf.org/downloads.html', 'danger')
        return redirect(url_for('leave.print_leave', leave_id=leave_id))
