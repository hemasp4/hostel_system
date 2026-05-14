from app import db
from datetime import datetime

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    category = db.Column(db.String(50))  # 'general', 'notification', 'qr'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value by key"""
        setting = SystemSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_setting(key, value, category='general', user_id=None):
        """Set or update a setting"""
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            setting.updated_by = user_id
        else:
            setting = SystemSettings(
                key=key,
                value=str(value),
                category=category,
                updated_by=user_id
            )
            db.session.add(setting)
        db.session.commit()
        return setting
    
    @staticmethod
    def get_all_settings():
        """Get all settings as a dictionary"""
        settings = SystemSettings.query.all()
        return {s.key: s.value for s in settings}
