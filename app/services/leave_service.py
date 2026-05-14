
from ..models.leave import LeaveRequest
from ..models.user import User
from .. import db
from .email_service import send_leave_request_email, send_leave_status_email
from .sms_service import send_leave_sms
from datetime import datetime

def create_leave_request(student_id, reason, start_date, end_date):
    """Create new leave request"""
    # Validate dates
    if start_date > end_date:
        return False, "End date must be after start date"
    
    if start_date < datetime.today().date():
        return False, "Cannot request leave for past dates"
    
    # Check for overlapping leaves
    overlapping = LeaveRequest.query.filter(
        LeaveRequest.student_id == student_id,
        LeaveRequest.status != 'rejected',
        LeaveRequest.start_date <= end_date,
        LeaveRequest.end_date >= start_date
    ).first()
    
    if overlapping:
        return False, "You have an overlapping leave request"
    
    leave = LeaveRequest(
        student_id=student_id,
        reason=reason,
        start_date=start_date,
        end_date=end_date
    )
    
    try:
        db.session.add(leave)
        db.session.commit()
        
        # Notify wardens
        wardens = User.query.filter_by(role='warden').all()
        student = User.query.get(student_id)
        
        for warden in wardens:
            send_leave_request_email(warden.email, student.name, leave)
        
        return True, leave
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def approve_leave(leave_id, approved_by_id):
    """Approve leave request"""
    leave = LeaveRequest.query.get(leave_id)
    if not leave:
        return False, "Leave request not found"
    
    if leave.status != 'pending':
        return False, "Leave request already processed"
    
    leave.status = 'approved'
    leave.approved_by = approved_by_id
    leave.approved_at = datetime.utcnow()
    
    # Generate QR code
    from .qr_service import generate_qr_code
    leave.qr_code = generate_qr_code(leave_id)
    
    try:
        db.session.commit()
        return True, leave
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def get_leave_statistics(student_id=None):
    """Get leave statistics"""
    query = LeaveRequest.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    total = query.count()
    approved = query.filter_by(status='approved').count()
    pending = query.filter_by(status='pending').count()
    rejected = query.filter_by(status='rejected').count()
    
    return {
        'total': total,
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'approval_rate': (approved / total * 100) if total > 0 else 0
    }
