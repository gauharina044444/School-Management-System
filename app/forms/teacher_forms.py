from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from wtforms.fields import DateTimeField, DateField

class AssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateTimeField('Due Date', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    points = FloatField('Points', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Assignment')

class TestForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateTimeField('Date & Time', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    duration = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    points = FloatField('Points', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Test')

class GradeForm(FlaskForm):
    assignment_id = SelectField('Assignment', coerce=int, validators=[Optional()])
    test_id = SelectField('Test', coerce=int, validators=[Optional()])
    points = FloatField('Points', validators=[DataRequired(), NumberRange(min=0)])
    comments = TextAreaField('Comments', validators=[Optional()])
    submit = SubmitField('Save Grade')

class AttendanceForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    status = SelectField('Status', validators=[DataRequired()], choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused')
    ])
    comment = TextAreaField('Comment', validators=[Optional()])
    submit = SubmitField('Save Attendance')