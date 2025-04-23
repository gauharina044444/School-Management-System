from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.subject import Subject
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.test import Test
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.models.user import User
from app.utils.access_control import teacher_required
from app.forms.teacher_forms import AssignmentForm, TestForm, GradeForm, AttendanceForm
from datetime import datetime, timedelta

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    # Get teacher's subjects
    subjects = current_user.teaching_subjects
    
    # Get upcoming assignments and tests
    upcoming_assignments = []
    upcoming_tests = []
    
    if subjects:
        # Get upcoming assignments and tests
        upcoming_assignments = Assignment.query.filter(
            Assignment.subject_id.in_([s.id for s in subjects]),
            Assignment.due_date >= datetime.now()
        ).order_by(Assignment.due_date).limit(5).all()
        
        upcoming_tests = Test.query.filter(
            Test.subject_id.in_([s.id for s in subjects]),
            Test.date >= datetime.now()
        ).order_by(Test.date).limit(5).all()
    
    # Count assignments and tests
    assignments_count = len(upcoming_assignments)
    tests_count = len(upcoming_tests)
    
    return render_template(
        'teacher/dashboard.html',
        subjects=subjects,
        upcoming_assignments=upcoming_assignments,
        upcoming_tests=upcoming_tests,
        assignments_count=assignments_count,
        tests_count=tests_count
    )

# Subjects
@teacher.route('/subjects')
@login_required
@teacher_required
def subjects_list():
    subjects = current_user.teaching_subjects
    return render_template('teacher/subjects/list.html', subjects=subjects)

@teacher.route('/subjects/<int:subject_id>')
@login_required
@teacher_required
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    students = subject.students
    assignments = subject.assignments
    tests = subject.tests
    
    return render_template(
        'teacher/subjects/detail.html',
        subject=subject,
        students=students,
        assignments=assignments,
        tests=tests
    )

# Assignments
@teacher.route('/subjects/<int:subject_id>/assignments')
@login_required
@teacher_required
def assignments_list(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    assignments = subject.assignments
    now = datetime.now()
    return render_template('teacher/assignments/list.html', subject=subject, assignments=assignments, now=now)

@teacher.route('/subjects/<int:subject_id>/assignments/new', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_assignment(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    form = AssignmentForm()
    
    if form.validate_on_submit():
        assignment = Assignment(
            subject_id=subject_id,
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            points=form.points.data
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        flash(f'Assignment "{assignment.title}" has been created successfully!', 'success')
        return redirect(url_for('teacher.assignments_list', subject_id=subject_id))
    
    return render_template(
        'teacher/assignments/form.html', 
        form=form, 
        subject=subject, 
        title='Create Assignment'
    )

@teacher.route('/assignments/<int:assignment_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    subject = assignment.subject
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    form = AssignmentForm(obj=assignment)
    
    if form.validate_on_submit():
        assignment.title = form.title.data
        assignment.description = form.description.data
        assignment.due_date = form.due_date.data
        assignment.points = form.points.data
        
        db.session.commit()
        
        flash(f'Assignment "{assignment.title}" has been updated successfully!', 'success')
        return redirect(url_for('teacher.assignments_list', subject_id=subject.id))
    
    return render_template(
        'teacher/assignments/form.html', 
        form=form, 
        subject=subject, 
        title='Edit Assignment'
    )

@teacher.route('/assignments/<int:assignment_id>/submissions')
@login_required
@teacher_required
def view_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    subject = assignment.subject
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not have permission to view submissions for this assignment.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).all()
    
    # Get all students enrolled in this subject
    students = subject.students
    
    # Map student ID to submission
    submission_map = {sub.student_id: sub for sub in submissions}
    
    # Get grades for this assignment
    grades = Grade.query.filter_by(assignment_id=assignment_id).all()
    
    # Map student ID to grade
    grade_map = {grade.student_id: grade for grade in grades}
    
    now = datetime.now()
    
    return render_template(
        'teacher/assignments/submissions.html',
        assignment=assignment,
        subject=subject,
        submissions=submissions,
        students=students,
        submission_map=submission_map,
        grade_map=grade_map,
        now=now
    )

@teacher.route('/submissions/<int:submission_id>')
@login_required
@teacher_required
def view_submission(submission_id):
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    assignment = submission.assignment
    subject = assignment.subject
    student = submission.student
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You do not have permission to view this submission.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    # Check if student has a grade for this assignment
    grade = Grade.query.filter_by(student_id=student.id, assignment_id=assignment.id).first()
    
    return render_template(
        'teacher/assignments/view_submission.html',
        submission=submission,
        assignment=assignment,
        subject=subject,
        student=student,
        grade=grade
    )

# Tests
@teacher.route('/subjects/<int:subject_id>/tests')
@login_required
@teacher_required
def tests_list(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    tests = subject.tests
    now = datetime.now()
    return render_template('teacher/tests/list.html', subject=subject, tests=tests, now=now)

@teacher.route('/subjects/<int:subject_id>/tests/new', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_test(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    form = TestForm()
    
    if form.validate_on_submit():
        test = Test(
            subject_id=subject_id,
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            duration=form.duration.data,
            points=form.points.data
        )
        
        db.session.add(test)
        db.session.commit()
        
        flash(f'Test "{test.title}" has been created successfully!', 'success')
        return redirect(url_for('teacher.tests_list', subject_id=subject_id))
    
    return render_template(
        'teacher/tests/form.html', 
        form=form, 
        subject=subject, 
        title='Create Test'
    )

@teacher.route('/tests/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_test(test_id):
    test = Test.query.get_or_404(test_id)
    subject = test.subject
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    form = TestForm(obj=test)
    
    if form.validate_on_submit():
        test.title = form.title.data
        test.description = form.description.data
        test.date = form.date.data
        test.duration = form.duration.data
        test.points = form.points.data
        
        db.session.commit()
        
        flash(f'Test "{test.title}" has been updated successfully!', 'success')
        return redirect(url_for('teacher.tests_list', subject_id=subject.id))
    
    return render_template(
        'teacher/tests/form.html', 
        form=form, 
        subject=subject, 
        title='Edit Test'
    )

@teacher.route('/tests/<int:test_id>/grades')
@login_required
@teacher_required
def test_grades(test_id):
    test = Test.query.get_or_404(test_id)
    subject = test.subject
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You do not have permission to view grades for this test.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    # Get all students enrolled in this subject
    students = subject.students
    
    # Get grades for this test
    grades = Grade.query.filter_by(test_id=test_id).all()
    
    # Map student ID to grade
    grade_map = {grade.student_id: grade for grade in grades}
    
    return render_template(
        'teacher/tests/grades.html',
        test=test,
        subject=subject,
        students=students,
        grades=grades,
        grade_map=grade_map
    )

# Grades
@teacher.route('/subjects/<int:subject_id>/grades')
@login_required
@teacher_required
def grades_list(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    students = subject.students
    
    # Get grades for each student
    student_grades = {}
    for student in students:
        grades = Grade.query.filter_by(student_id=student.id, subject_id=subject_id).all()
        student_grades[student.id] = grades
    
    return render_template(
        'teacher/grades/list.html', 
        subject=subject, 
        students=students,
        student_grades=student_grades
    )

@teacher.route('/grades/create/<int:subject_id>/<int:student_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_grade(subject_id, student_id):
    assignment_id = request.args.get('assignment_id', None)
    test_id = request.args.get('test_id', None)
    
    if assignment_id:
        assignment_id = int(assignment_id)
    if test_id:
        test_id = int(test_id)
    
    subject = Subject.query.get_or_404(subject_id)
    student = User.query.get_or_404(student_id)
    
    # Verify teacher is assigned to this subject and student is enrolled
    if subject not in current_user.teaching_subjects or subject not in student.enrolled_subjects:
        flash('You do not have permission to grade this student for this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    form = GradeForm()
    
    # Get assignments and tests for this subject
    form.assignment_id.choices = [(0, 'None')] + [(a.id, a.title) for a in subject.assignments]
    form.test_id.choices = [(0, 'None')] + [(t.id, t.title) for t in subject.tests]
    
    # Pre-select assignment or test if provided
    if assignment_id:
        form.assignment_id.data = assignment_id
    if test_id:
        form.test_id.data = test_id
    
    if form.validate_on_submit():
        # Convert 0 to None for assignment and test IDs
        assignment_id_val = form.assignment_id.data if form.assignment_id.data != 0 else None
        test_id_val = form.test_id.data if form.test_id.data != 0 else None
        
        grade = Grade(
            student_id=student_id,
            subject_id=subject_id,
            assignment_id=assignment_id_val,
            test_id=test_id_val,
            points=form.points.data,
            comments=form.comments.data
        )
        
        db.session.add(grade)
        db.session.commit()
        
        flash(f'Grade for {student.full_name} has been recorded!', 'success')
        
        # Redirect based on context
        if assignment_id:
            return redirect(url_for('teacher.view_submissions', assignment_id=assignment_id))
        elif test_id:
            return redirect(url_for('teacher.test_grades', test_id=test_id))
        else:
            return redirect(url_for('teacher.grades_list', subject_id=subject_id))
    
    return render_template(
        'teacher/grades/form.html', 
        form=form, 
        subject=subject, 
        student=student,
        title='Add Grade'
    )

@teacher.route('/grades/<int:grade_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    subject = grade.subject
    student = grade.student
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You do not have permission to edit this grade.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    form = GradeForm(obj=grade)
    
    # Get assignments and tests for this subject
    form.assignment_id.choices = [(0, 'None')] + [(a.id, a.title) for a in subject.assignments]
    form.test_id.choices = [(0, 'None')] + [(t.id, t.title) for t in subject.tests]
    
    # Set current values
    if grade.assignment_id:
        form.assignment_id.data = grade.assignment_id
    else:
        form.assignment_id.data = 0
        
    if grade.test_id:
        form.test_id.data = grade.test_id
    else:
        form.test_id.data = 0
    
    if form.validate_on_submit():
        # Convert 0 to None for assignment and test IDs
        assignment_id = form.assignment_id.data if form.assignment_id.data != 0 else None
        test_id = form.test_id.data if form.test_id.data != 0 else None
        
        grade.assignment_id = assignment_id
        grade.test_id = test_id
        grade.points = form.points.data
        grade.comments = form.comments.data
        
        db.session.commit()
        
        flash(f'Grade for {student.full_name} has been updated!', 'success')
        
        # Redirect based on where the grade edit was initiated from
        if grade.assignment_id:
            return redirect(url_for('teacher.view_submissions', assignment_id=grade.assignment_id))
        elif grade.test_id:
            return redirect(url_for('teacher.test_grades', test_id=grade.test_id))
        else:
            return redirect(url_for('teacher.grades_list', subject_id=subject.id))
    
    return render_template(
        'teacher/grades/form.html', 
        form=form, 
        subject=subject, 
        student=student,
        grade=grade,
        title='Edit Grade'
    )

# Attendance
@teacher.route('/subjects/<int:subject_id>/attendance')
@login_required
@teacher_required
def attendance_list(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    students = subject.students
    
    # Get date from query parameter or use today
    date_str = request.args.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = datetime.now().date()
    else:
        date = datetime.now().date()
    
    # Get attendance records for this subject on this date
    attendance_records = {}
    for student in students:
        record = Attendance.query.filter_by(
            student_id=student.id, 
            subject_id=subject_id,
            date=date
        ).first()
        
        attendance_records[student.id] = record
    
    # Get date navigation (previous week, next week)
    prev_date = date - timedelta(days=7)
    next_date = date + timedelta(days=7)
    
    return render_template(
        'teacher/attendance/list.html', 
        subject=subject, 
        students=students,
        attendance_records=attendance_records,
        date=date,
        prev_date=prev_date,
        next_date=next_date
    )

@teacher.route('/attendance/<int:attendance_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_attendance(attendance_id):
    attendance = Attendance.query.get_or_404(attendance_id)
    subject = Subject.query.get_or_404(attendance.subject_id)
    student = User.query.get_or_404(attendance.student_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You do not have permission to edit this attendance record.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    form = AttendanceForm(obj=attendance)
    
    if form.validate_on_submit():
        attendance.status = form.status.data
        attendance.comment = form.comment.data
        
        db.session.commit()
        
        flash('Attendance record has been updated successfully!', 'success')
        return redirect(url_for('teacher.attendance_list', subject_id=subject.id, date=attendance.date.strftime('%Y-%m-%d')))
    
    return render_template(
        'teacher/attendance/edit.html', 
        form=form, 
        subject=subject, 
        student=student,
        attendance=attendance,
        title='Edit Attendance'
    )

@teacher.route('/subjects/<int:subject_id>/attendance/take', methods=['GET', 'POST'])
@login_required
@teacher_required
def take_attendance(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify teacher is assigned to this subject
    if subject not in current_user.teaching_subjects:
        flash('You are not assigned to this subject.', 'danger')
        return redirect(url_for('teacher.subjects_list'))
    
    students = subject.students
    
    # Get date from form or use today
    date_str = request.args.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = datetime.now().date()
    else:
        date = datetime.now().date()
    
    if request.method == 'POST':
        # Process attendance data
        for student in students:
            status = request.form.get(f'status_{student.id}')
            comment = request.form.get(f'comment_{student.id}', '')
            
            # Check if record already exists
            record = Attendance.query.filter_by(
                student_id=student.id, 
                subject_id=subject_id,
                date=date
            ).first()
            
            if record:
                # Update existing record
                record.status = status
                record.comment = comment
            else:
                # Create new record
                record = Attendance(
                    student_id=student.id,
                    subject_id=subject_id,
                    date=date,
                    status=status,
                    comment=comment
                )
                db.session.add(record)
        
        db.session.commit()
        flash('Attendance has been recorded successfully!', 'success')
        return redirect(url_for('teacher.attendance_list', subject_id=subject_id, date=date.strftime('%Y-%m-%d')))
    
    # Get existing attendance records for this date
    attendance_records = {}
    for student in students:
        record = Attendance.query.filter_by(
            student_id=student.id, 
            subject_id=subject_id,
            date=date
        ).first()
        
        attendance_records[student.id] = record
    
    return render_template(
        'teacher/attendance/take.html', 
        subject=subject, 
        students=students,
        attendance_records=attendance_records,
        date=date
    )