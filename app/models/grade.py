from app import db
from datetime import datetime

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=True)
    points = db.Column(db.Float, nullable=False)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        grade_type = "General"
        if self.assignment_id:
            grade_type = "Assignment"
        elif self.test_id:
            grade_type = "Test"
        
        return f"{grade_type} Grade(Student: {self.student_id}, Subject: {self.subject_id}, Points: {self.points})"