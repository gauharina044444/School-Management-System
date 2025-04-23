from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Role
from app.models.school import School
from app.utils.access_control import super_admin_required
from app.forms.super_admin_forms import SchoolForm, AdminUserForm

super_admin = Blueprint('super_admin', __name__, url_prefix='/super-admin')

@super_admin.route('/dashboard')
@login_required
@super_admin_required
def dashboard():
    schools_count = School.query.count()
    admins_count = User.query.join(User.roles).filter(Role.name == 'admin').count()
    teachers_count = User.query.join(User.roles).filter(Role.name == 'teacher').count()
    students_count = User.query.join(User.roles).filter(Role.name == 'student').count()
    
    schools = School.query.order_by(School.name).all()
    
    return render_template(
        'super_admin/dashboard.html',
        schools_count=schools_count,
        admins_count=admins_count,
        teachers_count=teachers_count,
        students_count=students_count,
        schools=schools
    )

# Schools Management
@super_admin.route('/schools')
@login_required
@super_admin_required
def schools_list():
    schools = School.query.order_by(School.name).all()
    return render_template('super_admin/schools/list.html', schools=schools)

@super_admin.route('/schools/new', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_school():
    form = SchoolForm()
    
    if form.validate_on_submit():
        school = School(
            name=form.name.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            country=form.country.data,
            phone=form.phone.data,
            email=form.email.data,
            website=form.website.data,
            description=form.description.data
        )
        
        db.session.add(school)
        db.session.commit()
        
        flash(f'School "{school.name}" has been created successfully!', 'success')
        return redirect(url_for('super_admin.schools_list'))
    
    return render_template('super_admin/schools/form.html', form=form, title='Create School')

@super_admin.route('/schools/<int:school_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_school(school_id):
    school = School.query.get_or_404(school_id)
    form = SchoolForm(obj=school)
    
    if form.validate_on_submit():
        form.populate_obj(school)
        db.session.commit()
        
        flash(f'School "{school.name}" has been updated successfully!', 'success')
        return redirect(url_for('super_admin.schools_list'))
    
    return render_template('super_admin/schools/form.html', form=form, school=school, title='Edit School')

@super_admin.route('/schools/<int:school_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_school(school_id):
    school = School.query.get_or_404(school_id)
    
    # Check if school has any users
    if school.users:
        flash('Cannot delete school with associated users.', 'danger')
        return redirect(url_for('super_admin.schools_list'))
    
    db.session.delete(school)
    db.session.commit()
    
    flash(f'School "{school.name}" has been deleted.', 'success')
    return redirect(url_for('super_admin.schools_list'))

# Admin Users Management
@super_admin.route('/admins')
@login_required
@super_admin_required
def admins_list():
    admins = User.query.join(User.roles).filter(Role.name == 'admin').order_by(User.last_name).all()
    return render_template('super_admin/admins/list.html', admins=admins)

@super_admin.route('/admins/new', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_admin():
    form = AdminUserForm()
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    
    if form.validate_on_submit():
        admin_role = Role.query.filter_by(name='admin').first()
        
        admin = User(
            school_id=form.school_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            is_active=True
        )
        
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()
        
        flash(f'Administrator {admin.full_name} has been created successfully!', 'success')
        return redirect(url_for('super_admin.admins_list'))
    
    return render_template('super_admin/admins/form.html', form=form, title='Create Administrator')

@super_admin.route('/admins/<int:admin_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_admin(admin_id):
    admin = User.query.get_or_404(admin_id)
    
    # Verify this is actually an admin
    if not admin.is_admin():
        flash('User is not an administrator.', 'danger')
        return redirect(url_for('super_admin.admins_list'))
    
    form = AdminUserForm(obj=admin)
    form.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]
    
    # Don't require password for edit
    form.password.validators = []
    form.confirm_password.validators = []
    
    if form.validate_on_submit():
        admin.school_id = form.school_id.data
        admin.first_name = form.first_name.data
        admin.last_name = form.last_name.data
        admin.email = form.email.data
        
        if form.password.data:
            admin.set_password(form.password.data)
        
        db.session.commit()
        
        flash(f'Administrator {admin.full_name} has been updated successfully!', 'success')
        return redirect(url_for('super_admin.admins_list'))
    
    return render_template('super_admin/admins/form.html', form=form, admin=admin, title='Edit Administrator')

@super_admin.route('/admins/<int:admin_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_admin(admin_id):
    admin = User.query.get_or_404(admin_id)
    
    # Verify this is actually an admin
    if not admin.is_admin():
        flash('User is not an administrator.', 'danger')
        return redirect(url_for('super_admin.admins_list'))
    
    db.session.delete(admin)
    db.session.commit()
    
    flash(f'Administrator {admin.full_name} has been deleted.', 'success')
    return redirect(url_for('super_admin.admins_list'))