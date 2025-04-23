from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime

# Association tables
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

parent_student = db.Table('parent_student',
    db.Column('parent_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

teacher_subject = db.Table('teacher_subject',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

subject_enrollment = db.Table('subject_enrollment',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    
    def __repr__(self):
        return f"Role('{self.name}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary=user_roles, lazy='subquery',
                            backref=db.backref('users', lazy=True))
    school = db.relationship('School', backref='users')
    
    # Role-specific relationships
    children = db.relationship(
        'User',
        secondary=parent_student,
        primaryjoin=(parent_student.c.parent_id == id),
        secondaryjoin=(parent_student.c.student_id == id),
        backref=db.backref('parents', lazy='dynamic'),
        lazy='dynamic'
    )
    
    teaching_subjects = db.relationship(
        'Subject',
        secondary=teacher_subject,
        lazy='subquery',
        backref=db.backref('teachers', lazy=True)
    )
    
    enrolled_subjects = db.relationship(
        'Subject',
        secondary=subject_enrollment,
        lazy='subquery',
        backref=db.backref('students', lazy=True)
    )
    
    grades = db.relationship('Grade', backref='student', lazy=True,
                            foreign_keys='Grade.student_id')
    
    attendances = db.relationship('Attendance', backref='student', lazy=True,
                                foreign_keys='Attendance.student_id')
    
    def __init__(self, **kwargs):
        password = kwargs.pop('password', None)
        super(User, self).__init__(**kwargs)
        if password:
            self.set_password(password)
    
    def __repr__(self):
        return f"User('{self.email}', '{self.first_name} {self.last_name}')"
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def add_role(self, role):
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role):
        if role in self.roles:
            self.roles.remove(role)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    def is_super_admin(self):
        return self.has_role('super_admin')
    
    def is_admin(self):
        return self.has_role('admin')
    
    def is_teacher(self):
        return self.has_role('teacher')
    
    def is_student(self):
        return self.has_role('student')
    
    def is_parent(self):
        return self.has_role('parent')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))