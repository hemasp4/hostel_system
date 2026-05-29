from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..utils.decorators import role_required
from ..models.leave import LeaveRequest
from ..models.attendance import Attendance
from .. import db
from app.models.user import User

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    # Get student's recent leaves
    recent_leaves = LeaveRequest.query.filter_by(student_id=current_user.id)\
                                     .order_by(LeaveRequest.requested_at.desc())\
                                     .limit(5).all()
    
    # Get attendance stats
    total_leaves = LeaveRequest.query.filter_by(student_id=current_user.id).count()
    approved_leaves = LeaveRequest.query.filter_by(student_id=current_user.id, status='approved').count()
    
    return render_template('student/dashboard.html', 
                         recent_leaves=recent_leaves,
                         total_leaves=total_leaves,
                         approved_leaves=approved_leaves)
@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('student')
def profile():
    if request.method == 'POST':
        return update_profile()
    return render_template('student/profile.html', user=current_user)

@student_bp.route('/profile/update', methods=['POST'])
@login_required
@role_required('student')
def update_profile():
    """Update student profile"""
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate required fields
        if not name or not email or not phone:
            flash('Name, email, and phone are required fields', 'danger')
            return redirect(url_for('student.profile'))
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email address is already registered', 'danger')
            return redirect(url_for('student.profile'))
        
        # Update basic info
        current_user.name = name
        current_user.email = email
        current_user.phone = phone
        
        # Handle profile image upload
        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            import os
            from werkzeug.utils import secure_filename
            
            # Create uploads directory if not exists
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
            os.makedirs(upload_dir, exist_ok=True)
            
            ext = os.path.splitext(profile_image.filename)[1]
            filename = f"user_{current_user.id}{ext}"
            profile_image.save(os.path.join(upload_dir, filename))
            current_user.profile_image = filename
        
        # Update password if provided
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('student.profile'))
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return redirect(url_for('student.profile'))
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long', 'danger')
                return redirect(url_for('student.profile'))
            
            current_user.set_password(new_password)
            flash('Password updated successfully', 'success')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('student.profile'))
