from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default='student')  # student, warden, admin
    password_hash = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    profile_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leaves = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.student_id', 
                           backref='student', lazy='dynamic')
    approved_leaves = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.approved_by',
                                    backref='approver', lazy='dynamic')
    attendance_records = db.relationship('Attendance', foreign_keys='Attendance.student_id',
                                       backref='student', lazy='dynamic')
    scanned_attendance = db.relationship('Attendance', foreign_keys='Attendance.scanned_by',
                                       backref='scanner', lazy='dynamic')
    notifications = db.relationship('NotificationLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_role(self):
        return self.role
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_warden(self):
        return self.role == 'warden'
    
    def is_student(self):
        return self.role == 'student'
