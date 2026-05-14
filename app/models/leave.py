from app import db
from datetime import datetime

class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    qr_code = db.Column(db.Text, nullable=True)  # Base64 encoded QR image
    remarks = db.Column(db.Text, nullable=True)  # Warden/Admin remarks
    
    # Relationships are defined in User model using backref
    
    def __repr__(self):
        return f'<LeaveRequest {self.id}: {self.student_id} - {self.status}>'
    
    def get_duration(self):
        """Calculate leave duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0
    
    def is_active(self):
        """Check if leave is currently active"""
        today = datetime.today().date()
        return (self.status == 'approved' and 
                self.start_date <= today <= self.end_date)
