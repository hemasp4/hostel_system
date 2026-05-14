from app import db
from datetime import datetime

class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'email' or 'sms'
    recipient = db.Column(db.String(120), nullable=False)  # email or phone
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='sent')  # sent, failed, pending
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<NotificationLog {self.id}: {self.type} to {self.recipient}>'
