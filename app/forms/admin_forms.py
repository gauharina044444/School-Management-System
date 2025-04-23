from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField, SubmitField, FloatField, SelectMultipleField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from wtforms.fields import DateField
from app.models.user import User

class UserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Save User')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please choose a different one.')

class SubjectForm(FlaskForm):
    code = StringField('Subject Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    grade_level = StringField('Grade Level', validators=[Length(max=20)])
    credits = FloatField('Credits', validators=[NumberRange(min=0)])
    teachers = SelectMultipleField('Assign Teachers', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Subject')

class ScheduleForm(FlaskForm):
    name = StringField('Schedule Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Save Schedule')
    
    def validate_end_date(self, end_date):
        if end_date.data <= self.start_date.data:
            raise ValidationError('End date must be after start date.')

class ScheduleItemForm(FlaskForm):
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    day_of_week = SelectField('Day of Week', coerce=int, validators=[DataRequired()], choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ])
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    location = StringField('Location', validators=[Length(max=100)])
    submit = SubmitField('Save Schedule Item')
    
    def validate_end_time(self, end_time):
        if end_time.data <= self.start_time.data:
            raise ValidationError('End time must be after start time.')