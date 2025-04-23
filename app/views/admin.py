from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Role
from app.models.subject import Subject
from app.models.schedule import Schedule, ScheduleItem
from app.utils.access_control import admin_required
from app.forms.admin_forms import UserForm, SubjectForm, ScheduleForm, ScheduleItemForm, StudentEnrollmentForm

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    school = current_user.school
    
    teachers_count = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'teacher').count()
    students_count = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'student').count()
    parents_count = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'parent').count()
    subjects_count = Subject.query.filter_by(school_id=current_user.school_id).count()
    
    recent_teachers = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'teacher').order_by(User.created_at.desc()).limit(5).all()
    recent_students = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'student').order_by(User.created_at.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        school=school,
        teachers_count=teachers_count,
        students_count=students_count,
        parents_count=parents_count,
        subjects_count=subjects_count,
        recent_teachers=recent_teachers,
        recent_students=recent_students
    )

# Teachers Management
@admin.route('/teachers')
@login_required
@admin_required
def teachers_list():
    teachers = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'teacher').order_by(User.last_name).all()
    return render_template('admin/teachers/list.html', teachers=teachers)

@admin.route('/teachers/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_teacher():
    form = UserForm()
    
    if form.validate_on_submit():
        teacher_role = Role.query.filter_by(name='teacher').first()
        
        teacher = User(
            school_id=current_user.school_id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            is_active=True
        )
        
        teacher.roles.append(teacher_role)
        db.session.add(teacher)
        db.session.commit()
        
        flash(f'Teacher {teacher.full_name} has been created successfully!', 'success')
        return redirect(url_for('admin.teachers_list'))
    
    return render_template('admin/teachers/form.html', form=form, title='Create Teacher')

@admin.route('/teachers/<int:teacher_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)
    
    # Verify this is a teacher and belongs to current admin's school
    if not teacher.is_teacher() or teacher.school_id != current_user.school_id:
        flash('You do not have permission to edit this teacher.', 'danger')
        return redirect(url_for('admin.teachers_list'))
    
    form = UserForm(obj=teacher)
    
    # Don't require password for edit
    form.password.validators = []
    form.confirm_password.validators = []
    
    if form.validate_on_submit():
        teacher.first_name = form.first_name.data
        teacher.last_name = form.last_name.data
        teacher.email = form.email.data
        
        if form.password.data:
            teacher.set_password(form.password.data)
        
        db.session.commit()
        
        flash(f'Teacher {teacher.full_name} has been updated successfully!', 'success')
        return redirect(url_for('admin.teachers_list'))
    
    return render_template('admin/teachers/form.html', form=form, teacher=teacher, title='Edit Teacher')

# Students Management
@admin.route('/students')
@login_required
@admin_required
def students_list():
    students = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'student').order_by(User.last_name).all()
    return render_template('admin/students/list.html', students=students)

@admin.route('/students/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_student():
    form = UserForm()
    
    if form.validate_on_submit():
        student_role = Role.query.filter_by(name='student').first()
        
        student = User(
            school_id=current_user.school_id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            is_active=True
        )
        
        student.roles.append(student_role)
        db.session.add(student)
        db.session.commit()
        
        flash(f'Student {student.full_name} has been created successfully!', 'success')
        return redirect(url_for('admin.students_list'))
    
    return render_template('admin/students/form.html', form=form, title='Create Student')

@admin.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = User.query.get_or_404(student_id)
    
    # Verify this is a student and belongs to current admin's school
    if not student.is_student() or student.school_id != current_user.school_id:
        flash('You do not have permission to edit this student.', 'danger')
        return redirect(url_for('admin.students_list'))
    
    form = UserForm(obj=student)
    
    # Don't require password for edit
    form.password.validators = []
    form.confirm_password.validators = []
    
    if form.validate_on_submit():
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.email = form.email.data
        
        if form.password.data:
            student.set_password(form.password.data)
        
        db.session.commit()
        
        flash(f'Student {student.full_name} has been updated successfully!', 'success')
        return redirect(url_for('admin.students_list'))
    
    return render_template('admin/students/form.html', form=form, student=student, title='Edit Student')

# Subjects Management
@admin.route('/subjects')
@login_required
@admin_required
def subjects_list():
    subjects = Subject.query.filter_by(school_id=current_user.school_id).order_by(Subject.name).all()
    return render_template('admin/subjects/list.html', subjects=subjects)

@admin.route('/subjects/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_subject():
    try:
        form = SubjectForm()
        
        # Get teachers for this school
        teachers = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'teacher').all()
        form.teachers.choices = [(t.id, t.full_name) for t in teachers]
        
        # Get students for this school
        students = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'student').order_by(User.last_name).all()
        form.students.choices = [(s.id, f"{s.full_name} ({s.email})") for s in students]
        
        if form.validate_on_submit():
            subject = Subject(
                school_id=current_user.school_id,
                code=form.code.data,
                name=form.name.data,
                description=form.description.data,
                grade_level=form.grade_level.data,
                credits=form.credits.data
            )
            
            # Add teachers
            for teacher_id in form.teachers.data:
                teacher = User.query.get(teacher_id)
                if teacher and teacher.is_teacher():
                    subject.teachers.append(teacher)
            
            # Add students
            if form.students and form.students.data:
                for student_id in form.students.data:
                    student = User.query.get(student_id)
                    if student and student.is_student():
                        subject.students.append(student)
            
            db.session.add(subject)
            db.session.commit()
            
            flash(f'Subject "{subject.name}" has been created successfully!', 'success')
            return redirect('/admin/subjects')
        
        return render_template('admin/subjects/form.html', form=form, title='Create Subject')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect('/admin/subjects')

@admin.route('/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Verify subject belongs to admin's school
        if subject.school_id != current_user.school_id:
            flash('You do not have permission to edit this subject.', 'danger')
            return redirect('/admin/subjects')
        
        form = SubjectForm(obj=subject)
        
        # Get teachers for this school
        teachers = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'teacher').all()
        form.teachers.choices = [(t.id, t.full_name) for t in teachers]
        
        # Get students for this school
        students = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'student').order_by(User.last_name).all()
        form.students.choices = [(s.id, f"{s.full_name} ({s.email})") for s in students]
        
        # Pre-select current teachers and students
        if request.method == 'GET':
            form.teachers.data = [teacher.id for teacher in subject.teachers]
            form.students.data = [student.id for student in subject.students]
        
        if form.validate_on_submit():
            subject.code = form.code.data
            subject.name = form.name.data
            subject.description = form.description.data
            subject.grade_level = form.grade_level.data
            subject.credits = form.credits.data
            
            # Update teachers
            subject.teachers = []
            for teacher_id in form.teachers.data:
                teacher = User.query.get(teacher_id)
                if teacher and teacher.is_teacher():
                    subject.teachers.append(teacher)
            
            # Update students
            subject.students = []
            if form.students and form.students.data:
                for student_id in form.students.data:
                    student = User.query.get(student_id)
                    if student and student.is_student():
                        subject.students.append(student)
            
            db.session.commit()
            
            flash(f'Subject "{subject.name}" has been updated successfully!', 'success')
            return redirect('/admin/subjects')
        
        return render_template('admin/subjects/form.html', form=form, subject=subject, title='Edit Subject')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect('/admin/subjects')

# Keep this route for compatibility
@admin.route('/subjects/<int:subject_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_subject(subject_id):
    return redirect(f'/admin/subjects/{subject_id}/edit')

@admin.route('/subjects/<int:subject_id>/students', methods=['GET', 'POST'])
@login_required
@admin_required
def subject_students(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Verify subject belongs to admin's school
    if subject.school_id != current_user.school_id:
        flash('You do not have permission to view this subject.', 'danger')
        return redirect(url_for('admin.subjects_list'))
    
    students = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'student').order_by(User.last_name).all()
    
    # Get IDs of enrolled students
    enrolled_student_ids = [student.id for student in subject.students]
    
    # Create form for batch enrollment
    batch_form = StudentEnrollmentForm()
    
    # Get available students for the form choices
    available_students = [s for s in students if s.id not in enrolled_student_ids]
    batch_form.student_ids.choices = [(s.id, f"{s.full_name} ({s.email})") for s in available_students]
    
    if batch_form.validate_on_submit():
        added_count = 0
        for student_id in batch_form.student_ids.data:
            student = User.query.get(student_id)
            # Verify this is a valid student at this school
            if student and student.is_student() and student.school_id == current_user.school_id:
                # Check if not already enrolled
                if student not in subject.students:
                    subject.students.append(student)
                    added_count += 1
        
        if added_count > 0:
            db.session.commit()
            flash(f'Successfully enrolled {added_count} students in {subject.name}.', 'success')
            return redirect(url_for('admin.subject_students', subject_id=subject_id))
        else:
            flash('No new students were enrolled. They may already be enrolled or invalid selections were made.', 'warning')
    
    return render_template(
        'admin/subjects/students.html',
        subject=subject,
        students=students,
        enrolled_student_ids=enrolled_student_ids,
        batch_form=batch_form,
        available_students=available_students
    )

@admin.route('/subjects/<int:subject_id>/students/add', methods=['POST'])
@login_required
@admin_required
def add_student_to_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Verify subject belongs to admin's school
        if subject.school_id != current_user.school_id:
            flash('You do not have permission to modify this subject.', 'danger')
            return redirect(url_for('admin.subjects_list'))
        
        student_id = request.form.get('student_id')
        if not student_id:
            flash('No student selected.', 'danger')
            return redirect(url_for('admin.subject_students', subject_id=subject_id))
        
        student = User.query.get_or_404(int(student_id))
        
        # Check if student belongs to this school and has student role
        if student.school_id != current_user.school_id or not student.is_student():
            flash('Invalid student selection.', 'danger')
            return redirect(url_for('admin.subject_students', subject_id=subject_id))
        
        # Check if student is already enrolled
        if student in subject.students:
            flash(f'Student {student.full_name} is already enrolled in this subject.', 'warning')
        else:
            subject.students.append(student)
            db.session.commit()
            flash(f'Student {student.full_name} has been enrolled in {subject.name}.', 'success')
        
        return redirect(url_for('admin.subject_students', subject_id=subject_id))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin.subjects_list'))

@admin.route('/subjects/<int:subject_id>/students/<int:student_id>/remove', methods=['POST'])
@login_required
@admin_required
def remove_student_from_subject(subject_id, student_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Verify subject belongs to admin's school
        if subject.school_id != current_user.school_id:
            flash('You do not have permission to modify this subject.', 'danger')
            return redirect(url_for('admin.subjects_list'))
        
        student = User.query.get_or_404(student_id)
        
        # Check if student is enrolled
        if student not in subject.students:
            flash(f'Student {student.full_name} is not enrolled in this subject.', 'warning')
        else:
            subject.students.remove(student)
            db.session.commit()
            flash(f'Student {student.full_name} has been removed from {subject.name}.', 'success')
        
        return redirect(url_for('admin.subject_students', subject_id=subject_id))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin.subjects_list'))

# Schedules Management
@admin.route('/schedules')
@login_required
@admin_required
def schedules_list():
    schedules = Schedule.query.filter_by(school_id=current_user.school_id).order_by(Schedule.start_date.desc()).all()
    return render_template('admin/schedules/list.html', schedules=schedules)

@admin.route('/schedules/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_schedule():
    form = ScheduleForm()
    
    if form.validate_on_submit():
        schedule = Schedule(
            school_id=current_user.school_id,
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        flash(f'Schedule "{schedule.name}" has been created successfully!', 'success')
        return redirect(url_for('admin.schedules_list'))
    
    return render_template('admin/schedules/form.html', form=form, title='Create Schedule')

@admin.route('/schedules/<int:schedule_id>/items')
@login_required
@admin_required
def schedule_items_list(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verify schedule belongs to current admin's school
    if schedule.school_id != current_user.school_id:
        flash('You do not have permission to view this schedule.', 'danger')
        return redirect(url_for('admin.schedules_list'))
    
    items = ScheduleItem.query.filter_by(schedule_id=schedule_id).order_by(ScheduleItem.day_of_week, ScheduleItem.start_time).all()
    return render_template('admin/schedules/items.html', schedule=schedule, items=items)

@admin.route('/schedules/<int:schedule_id>/items/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_schedule_item(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verify schedule belongs to current admin's school
    if schedule.school_id != current_user.school_id:
        flash('You do not have permission to modify this schedule.', 'danger')
        return redirect(url_for('admin.schedules_list'))
    
    form = ScheduleItemForm()
    
    # Get subjects for this school
    subjects = Subject.query.filter_by(school_id=current_user.school_id).all()
    form.subject_id.choices = [(s.id, f"{s.code} - {s.name}") for s in subjects]
    
    if form.validate_on_submit():
        item = ScheduleItem(
            schedule_id=schedule_id,
            subject_id=form.subject_id.data,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            location=form.location.data
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('Schedule item has been added successfully!', 'success')
        return redirect(url_for('admin.schedule_items_list', schedule_id=schedule_id))
    
    return render_template(
        'admin/schedules/item_form.html', 
        form=form, 
        schedule=schedule, 
        title='Add Schedule Item'
    )

# Parents Management
@admin.route('/parents')
@login_required
@admin_required
def parents_list():
    parents = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(Role.name == 'parent').order_by(User.last_name).all()
    return render_template('admin/parents/list.html', parents=parents)

@admin.route('/parents/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_parent():
    form = UserForm()
    
    if form.validate_on_submit():
        parent_role = Role.query.filter_by(name='parent').first()
        
        parent = User(
            school_id=current_user.school_id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            is_active=True
        )
        
        parent.roles.append(parent_role)
        db.session.add(parent)
        db.session.commit()
        
        flash(f'Parent {parent.full_name} has been created successfully!', 'success')
        return redirect(url_for('admin.parents_list'))
    
    return render_template('admin/parents/form.html', form=form, title='Create Parent')

@admin.route('/parents/<int:parent_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_parent(parent_id):
    parent = User.query.get_or_404(parent_id)
    
    # Verify this is a parent and belongs to current admin's school
    if not parent.is_parent() or parent.school_id != current_user.school_id:
        flash('You do not have permission to edit this parent.', 'danger')
        return redirect(url_for('admin.parents_list'))
    
    form = UserForm(obj=parent)
    
    # Don't require password for edit
    form.password.validators = []
    form.confirm_password.validators = []
    
    if form.validate_on_submit():
        parent.first_name = form.first_name.data
        parent.last_name = form.last_name.data
        parent.email = form.email.data
        
        if form.password.data:
            parent.set_password(form.password.data)
        
        db.session.commit()
        
        flash(f'Parent {parent.full_name} has been updated successfully!', 'success')
        return redirect(url_for('admin.parents_list'))
    
    return render_template('admin/parents/form.html', form=form, parent=parent, title='Edit Parent')

@admin.route('/parents/<int:parent_id>/children', methods=['GET'])
@login_required
@admin_required
def parent_children(parent_id):
    parent = User.query.get_or_404(parent_id)
    
    # Verify this is a parent and belongs to current admin's school
    if not parent.is_parent() or parent.school_id != current_user.school_id:
        flash('You do not have permission to view this parent.', 'danger')
        return redirect(url_for('admin.parents_list'))
    
    children = parent.children.all()
    
    return render_template('admin/parents/children.html', parent=parent, children=children)

@admin.route('/parents/<int:parent_id>/associate-child', methods=['GET', 'POST'])
@login_required
@admin_required
def associate_child(parent_id):
    parent = User.query.get_or_404(parent_id)
    
    # Verify this is a parent and belongs to current admin's school
    if not parent.is_parent() or parent.school_id != current_user.school_id:
        flash('You do not have permission to modify this parent.', 'danger')
        return redirect(url_for('admin.parents_list'))
    
    # Get all students that aren't already associated with this parent
    existing_child_ids = [child.id for child in parent.children]
    available_students = User.query.filter_by(school_id=current_user.school_id).join(User.roles).filter(
        Role.name == 'student',
        ~User.id.in_(existing_child_ids) if existing_child_ids else True
    ).all()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        if student_id:
            student = User.query.get_or_404(int(student_id))
            if student.is_student() and student.school_id == current_user.school_id:
                parent.children.append(student)
                db.session.commit()
                flash(f'Student {student.full_name} has been associated with parent {parent.full_name}.', 'success')
                return redirect(url_for('admin.parent_children', parent_id=parent_id))
    
    return render_template(
        'admin/parents/associate_child.html',
        parent=parent,
        available_students=available_students
    )

@admin.route('/parents/<int:parent_id>/remove-child/<int:child_id>', methods=['POST'])
@login_required
@admin_required
def remove_child(parent_id, child_id):
    parent = User.query.get_or_404(parent_id)
    child = User.query.get_or_404(child_id)
    
    # Verify this is a parent and belongs to current admin's school
    if not parent.is_parent() or parent.school_id != current_user.school_id:
        flash('You do not have permission to modify this parent.', 'danger')
        return redirect(url_for('admin.parents_list'))
    
    # Verify child belongs to this parent
    if child not in parent.children:
        flash('This child is not associated with this parent.', 'danger')
        return redirect(url_for('admin.parent_children', parent_id=parent_id))
    
    parent.children.remove(child)
    db.session.commit()
    
    flash(f'Child {child.full_name} has been removed from parent {parent.full_name}.', 'success')
    return redirect(url_for('admin.parent_children', parent_id=parent_id))