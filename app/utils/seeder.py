from app import db, bcrypt
from app.models.user import User, Role
from app.models.school import School
import os

def create_roles():
    """Create default roles if they don't exist."""
    roles = ['super_admin', 'admin', 'teacher', 'student', 'parent']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    
    db.session.commit()

def create_super_admin():
    """Create a super admin user if one doesn't exist."""
    if not User.query.join(User.roles).filter(Role.name == 'super_admin').first():
        super_admin_role = Role.query.filter_by(name='super_admin').first()
        
        # Use environment variables or default values for super admin credentials
        email = os.environ.get('SUPER_ADMIN_EMAIL', 'admin@schoolsystem.com')
        password = os.environ.get('SUPER_ADMIN_PASSWORD', 'Admin123!')
        
        super_admin = User(
            first_name='Super',
            last_name='Admin',
            email=email,
            password=password,
            is_active=True
        )
        
        super_admin.roles.append(super_admin_role)
        db.session.add(super_admin)
        db.session.commit()

def create_demo_data():
    """Create demo data for testing purposes."""
    # Only create demo data if there are no schools
    if School.query.first():
        return
    
    # Create a demo school
    demo_school = School(
        name='Demo High School',
        address='123 Main Street',
        city='Anytown',
        state='State',
        zip_code='12345',
        country='Country',
        phone='(123) 456-7890',
        email='info@demohighschool.edu',
        website='www.demohighschool.edu',
        description='A demo high school for testing purposes.'
    )
    db.session.add(demo_school)
    db.session.flush()  # Get the school ID
    
    # Create school admin
    admin_role = Role.query.filter_by(name='admin').first()
    admin = User(
        school_id=demo_school.id,
        first_name='School',
        last_name='Admin',
        email='schooladmin@demohighschool.edu',
        password='Password123!',
        is_active=True
    )
    admin.roles.append(admin_role)
    db.session.add(admin)
    
    # Create teachers
    teacher_role = Role.query.filter_by(name='teacher').first()
    for i in range(1, 4):
        teacher = User(
            school_id=demo_school.id,
            first_name=f'Teacher{i}',
            last_name='Demo',
            email=f'teacher{i}@demohighschool.edu',
            password='Password123!',
            is_active=True
        )
        teacher.roles.append(teacher_role)
        db.session.add(teacher)
    
    # Create students
    student_role = Role.query.filter_by(name='student').first()
    for i in range(1, 11):
        student = User(
            school_id=demo_school.id,
            first_name=f'Student{i}',
            last_name='Demo',
            email=f'student{i}@demohighschool.edu',
            password='Password123!',
            is_active=True
        )
        student.roles.append(student_role)
        db.session.add(student)
    
    # Create parents
    parent_role = Role.query.filter_by(name='parent').first()
    for i in range(1, 6):
        parent = User(
            school_id=demo_school.id,
            first_name=f'Parent{i}',
            last_name='Demo',
            email=f'parent{i}@example.com',
            password='Password123!',
            is_active=True
        )
        parent.roles.append(parent_role)
        db.session.add(parent)
    
    db.session.commit()