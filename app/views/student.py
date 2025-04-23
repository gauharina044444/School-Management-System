from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models.subject import Subject
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.test import Test
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.utils.access_control import student_required
from app.forms.student_forms import AssignmentSubmissionForm
from datetime import datetime, timedelta
import os

student = Blueprint('student', __name__, url_prefix='/student')

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Get student's subjects
    subjects = current_user.enrolled_subjects
    
    # Get upcoming assignments
    upcoming_assignments = Assignment.query.filter(
        Assignment.subject_id.in_([s.id for s in subjects]),
        Assignment.due_date >= datetime.now()
    ).order_by(Assignment.due_date).limit(5).all()
    
    # Get upcoming tests
    upcoming_tests = Test.query.filter(
        Test.subject_id.in_([s.id for s in subjects]),
        Test.date >= datetime.now()
    ).order_by(Test.date).limit(5).all()
    
    # Get recent grades
    recent_grades = Grade.query.filter_by(student_id=current_user.id).order_by(Grade.created_at.desc()).limit(5).all()
    
    return render_template(
        'student/dashboard.html',
        subjects=subjects,
        upcoming_assignments=upcoming_assignments,
        upcoming_tests=upcoming_tests,
        recent_grades=recent_grades
    )

# Subjects
@student.route('/subjects')
@login_required
@student_required
def subjects_list():
    subjects = current_user.enrolled_subjects
    return render_template('student/subjects/list.html', subjects=subjects)

@student.route('/subjects/<int:subject_id>')
@login_required
@student_required
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify student is enrolled in this subject
    if subject not in current_user.enrolled_subjects:
        flash('You are not enrolled in this subject.', 'danger')
        return redirect(url_for('student.subjects_list'))
    
    # Get assignments and tests
    assignments = subject.assignments
    tests = subject.tests
    
    # Get teacher information
    teachers = subject.teachers
    
    return render_template(
        'student/subjects/detail.html',
        subject=subject,
        assignments=assignments,
        tests=tests,
        teachers=teachers
    )

# Assignments
@student.route('/assignments')
@login_required
@student_required
def assignments_list():
    # Get filter parameters
    status = request.args.get('status', 'all')
    subject_id = request.args.get('subject_id')
    
    # Get student's subjects
    subjects = current_user.enrolled_subjects
    subject_ids = [s.id for s in subjects]
    
    # Apply subject filter if provided
    selected_subject = None
    if subject_id and subject_id != 'None':
        try:
            subject_id = int(subject_id)
            if subject_id in subject_ids:
                subject_ids = [subject_id]
                selected_subject = Subject.query.get(subject_id)
        except ValueError:
            pass
    
    # Get all assignments for these subjects
    assignments = Assignment.query.filter(Assignment.subject_id.in_(subject_ids)).order_by(Assignment.due_date).all()
    
    # Get submission status and grades for each assignment
    submission_map = {}
    grade_map = {}
    now = datetime.now()
    
    for assignment in assignments:
        # Get submission
        submission = AssignmentSubmission.query.filter_by(
            assignment_id=assignment.id, 
            student_id=current_user.id
        ).first()
        
        if submission:
            submission_map[assignment.id] = submission
        
        # Get grade
        grade = Grade.query.filter_by(
            assignment_id=assignment.id,
            student_id=current_user.id
        ).first()
        
        if grade:
            grade_map[assignment.id] = grade
    
    # Apply status filter
    filtered_assignments = []
    for assignment in assignments:
        if status == 'all':
            filtered_assignments.append(assignment)
        elif status == 'pending' and assignment.id not in submission_map:
            filtered_assignments.append(assignment)
        elif status == 'submitted' and assignment.id in submission_map:
            filtered_assignments.append(assignment)
        elif status == 'graded' and assignment.id in grade_map:
            filtered_assignments.append(assignment)
    
    return render_template(
        'student/assignments/list.html',
        subject=selected_subject,
        subjects=subjects,
        assignments=filtered_assignments,
        submission_map=submission_map,
        grade_map=grade_map,
        filter_status=status,
        now=now
    )

@student.route('/assignments/<int:assignment_id>')
@login_required
@student_required
def assignment_detail(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Verify student is enrolled in this subject
    if assignment.subject not in current_user.enrolled_subjects:
        flash('You do not have access to this assignment.', 'danger')
        return redirect(url_for('student.assignments_list'))
    
    # Get submission if it exists
    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment.id, 
        student_id=current_user.id
    ).first()
    
    # Check for grade
    grade = Grade.query.filter_by(
        assignment_id=assignment.id, 
        student_id=current_user.id
    ).first()
    
    return render_template(
        'student/assignments/detail.html',
        assignment=assignment,
        submission=submission,
        grade=grade
    )

@student.route('/assignments/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
@student_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Verify student is enrolled in this subject
    if assignment.subject not in current_user.enrolled_subjects:
        flash('You do not have access to this assignment.', 'danger')
        return redirect(url_for('student.assignments_list'))
    
    # Check if already submitted
    existing_submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment.id, 
        student_id=current_user.id
    ).first()
    
    if existing_submission:
        flash('You have already submitted this assignment. Please edit your submission instead.', 'warning')
        return redirect(url_for('student.assignment_detail', assignment_id=assignment.id))
    
    form = AssignmentSubmissionForm()
    
    if form.validate_on_submit():
        # Check if submission is late
        is_late = datetime.now() > assignment.due_date
        
        submission = AssignmentSubmission(
            assignment_id=assignment.id,
            student_id=current_user.id,
            submission_text=form.submission_text.data,
            is_late=is_late
        )
        
        db.session.add(submission)
        db.session.commit()
        
        flash('Your assignment has been submitted successfully!', 'success')
        return redirect(url_for('student.assignment_detail', assignment_id=assignment.id))
    
    return render_template(
        'student/assignments/submit.html',
        form=form,
        assignment=assignment
    )

# Tests
@student.route('/tests')
@login_required
@student_required
def tests_list():
    # Get student's subjects
    subjects = current_user.enrolled_subjects
    subject_ids = [s.id for s in subjects]
    
    # Get all tests for these subjects
    tests = Test.query.filter(Test.subject_id.in_(subject_ids)).order_by(Test.date).all()
    
    # Group tests by subject
    tests_by_subject = {}
    for subject in subjects:
        tests_by_subject[subject.id] = []
    
    for test in tests:
        tests_by_subject[test.subject_id].append(test)
    
    # Get grade for each test
    test_grades = {}
    for test in tests:
        grade = Grade.query.filter_by(
            test_id=test.id, 
            student_id=current_user.id
        ).first()
        
        test_grades[test.id] = grade
    
    return render_template(
        'student/tests/list.html',
        subjects=subjects,
        tests_by_subject=tests_by_subject,
        test_grades=test_grades
    )

# Grades
@student.route('/grades')
@login_required
@student_required
def grades_list():
    # Get student's subjects
    subjects = current_user.enrolled_subjects
    
    # Get all grades grouped by subject
    grades_by_subject = {}
    for subject in subjects:
        grades = Grade.query.filter_by(
            student_id=current_user.id,
            subject_id=subject.id
        ).all()
        
        grades_by_subject[subject.id] = grades
    
    return render_template(
        'student/grades/list.html',
        subjects=subjects,
        grades_by_subject=grades_by_subject
    )

# Submissions
@student.route('/submissions/<int:submission_id>/download')
@login_required
def download_submission(submission_id):
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    
    # Security checks
    if current_user.id != submission.student_id and not current_user.is_teacher() and not current_user.is_admin():
        flash('You do not have permission to download this file.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # If user is a teacher, verify they teach this subject
    if current_user.is_teacher() and submission.assignment.subject not in current_user.teaching_subjects:
        flash('You do not have permission to download this file.', 'danger')
        return redirect(url_for('teacher.dashboard'))
    
    # If file doesn't exist, return an error
    if not submission.file_path or not os.path.exists(submission.file_path):
        flash('The requested file does not exist.', 'danger')
        if current_user.is_teacher():
            return redirect(url_for('teacher.view_submission', submission_id=submission.id))
        else:
            return redirect(url_for('student.assignment_detail', assignment_id=submission.assignment_id))
    
    # Get the file name from the path
    filename = os.path.basename(submission.file_path)
    
    # Send the file to the user
    return send_file(
        submission.file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream'
    )

# Attendance
@student.route('/attendance')
@login_required
@student_required
def attendance_list():
    # Get student's subjects
    subjects = current_user.enrolled_subjects
    
    # Get attendance records for each subject
    attendance_by_subject = {}
    for subject in subjects:
        records = Attendance.query.filter_by(
            student_id=current_user.id,
            subject_id=subject.id
        ).order_by(Attendance.date.desc()).all()
        
        attendance_by_subject[subject.id] = records
    
    return render_template(
        'student/attendance/list.html',
        subjects=subjects,
        attendance_by_subject=attendance_by_subject
    )