from app import db
from datetime import datetime

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    grade_level = db.Column(db.String(20))
    credits = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='subject', lazy=True)
    tests = db.relationship('Test', backref='subject', lazy=True)
    attendances = db.relationship('Attendance', backref='subject', lazy=True)
    grades = db.relationship('Grade', backref='subject', lazy=True,
                           foreign_keys='Grade.subject_id')
    schedule_items = db.relationship('ScheduleItem', backref='subject', lazy=True)
    
    # Relationships for teachers and students are defined in User model via association tables
    
    def __repr__(self):
        return f"Subject('{self.code}', '{self.name}')"