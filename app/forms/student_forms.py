from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class AssignmentSubmissionForm(FlaskForm):
    submission_text = TextAreaField('Submission', validators=[DataRequired()])
    submit = SubmitField('Submit Assignment')