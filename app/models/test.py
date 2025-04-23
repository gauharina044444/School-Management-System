from app import db
from datetime import datetime

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    points = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    grades = db.relationship('Grade', backref='test', lazy=True,
                           foreign_keys='Grade.test_id')
    
    def __repr__(self):
        return f"Test('{self.title}', on '{self.date}')"