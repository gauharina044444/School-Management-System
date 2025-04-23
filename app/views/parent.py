from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.utils.access_control import parent_required
from datetime import datetime, timedelta

parent = Blueprint('parent', __name__, url_prefix='/parent')

@parent.route('/dashboard')
@login_required
@parent_required
def dashboard():
    # Get parent's children
    children = current_user.children.all()
    
    # Get recent grades for each child
    recent_grades = {}
    for child in children:
        grades = Grade.query.filter_by(student_id=child.id).order_by(Grade.created_at.desc()).limit(5).all()
        recent_grades[child.id] = grades
    
    # Get recent attendance for each child
    recent_attendance = {}
    for child in children:
        attendance = Attendance.query.filter_by(student_id=child.id).order_by(Attendance.date.desc()).limit(5).all()
        recent_attendance[child.id] = attendance
    
    return render_template(
        'parent/dashboard.html',
        children=children,
        recent_grades=recent_grades,
        recent_attendance=recent_attendance
    )

@parent.route('/children')
@login_required
@parent_required
def children_list():
    children = current_user.children.all()
    return render_template('parent/children/list.html', children=children)

@parent.route('/children/<int:child_id>')
@login_required
@parent_required
def child_detail(child_id):
    # Verify this is actually the user's child
    child = User.query.get_or_404(child_id)
    if child not in current_user.children:
        flash('You do not have access to view this student.', 'danger')
        return redirect(url_for('parent.children_list'))
    
    # Get child's subjects
    subjects = child.enrolled_subjects
    
    return render_template(
        'parent/children/detail.html',
        child=child,
        subjects=subjects
    )

@parent.route('/children/<int:child_id>/grades')
@login_required
@parent_required
def child_grades(child_id):
    # Verify this is actually the user's child
    child = User.query.get_or_404(child_id)
    if child not in current_user.children:
        flash('You do not have access to view this student.', 'danger')
        return redirect(url_for('parent.children_list'))
    
    # Get child's subjects
    subjects = child.enrolled_subjects
    
    # Get all grades grouped by subject
    grades_by_subject = {}
    for subject in subjects:
        grades = Grade.query.filter_by(
            student_id=child.id,
            subject_id=subject.id
        ).all()
        
        grades_by_subject[subject.id] = grades
    
    return render_template(
        'parent/children/grades.html',
        child=child,
        subjects=subjects,
        grades_by_subject=grades_by_subject
    )

@parent.route('/children/<int:child_id>/attendance')
@login_required
@parent_required
def child_attendance(child_id):
    # Verify this is actually the user's child
    child = User.query.get_or_404(child_id)
    if child not in current_user.children:
        flash('You do not have access to view this student.', 'danger')
        return redirect(url_for('parent.children_list'))
    
    # Get child's subjects
    subjects = child.enrolled_subjects
    
    # Get attendance records for each subject
    attendance_by_subject = {}
    for subject in subjects:
        records = Attendance.query.filter_by(
            student_id=child.id,
            subject_id=subject.id
        ).order_by(Attendance.date.desc()).all()
        
        attendance_by_subject[subject.id] = records
    
    return render_template(
        'parent/children/attendance.html',
        child=child,
        subjects=subjects,
        attendance_by_subject=attendance_by_subject
    )