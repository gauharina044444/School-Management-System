from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, URL
from app.models.user import User

class SchoolForm(FlaskForm):
    name = StringField('School Name', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[Length(max=200)])
    city = StringField('City', validators=[Length(max=50)])
    state = StringField('State', validators=[Length(max=50)])
    zip_code = StringField('ZIP Code', validators=[Length(max=20)])
    country = StringField('Country', validators=[Length(max=50)])
    phone = StringField('Phone', validators=[Length(max=20)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    website = StringField('Website', validators=[Optional(), URL(), Length(max=120)])
    description = TextAreaField('Description')
    submit = SubmitField('Save School')

class AdminUserForm(FlaskForm):
    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
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
    submit = SubmitField('Save Administrator')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please choose a different one.')
            
    # This validation will only run on form creation, not edit
    def validate_password(self, password):
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
            
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
            
        # Check for at least one digit
        if not any(c.isdigit() for c in password.data):
            raise ValidationError('Password must contain at least one number.')
            
        # Check for at least one special character
        special_chars = "!@#$%^&*()-_=+[]{};:,.<>?/|`~"
        if not any(c in special_chars for c in password.data):
            raise ValidationError('Password must contain at least one special character.')