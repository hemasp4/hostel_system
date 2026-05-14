from app import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leave_id = db.Column(db.Integer, db.ForeignKey('leave_requests.id'), nullable=False)
    scan_type = db.Column(db.String(10), nullable=False)  # 'exit' or 'entry'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    scanned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location = db.Column(db.String(100), default='Main Gate')
    
    # Relationships
    leave = db.relationship('LeaveRequest', backref='attendance_records')
    
    def __repr__(self):
        return f'<Attendance {self.id}: Student {self.student_id} - {self.scan_type}>'
