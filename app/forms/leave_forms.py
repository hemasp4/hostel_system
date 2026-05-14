from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length

class LeaveRequestForm(FlaskForm):
    reason = TextAreaField('Reason for Leave', 
                          validators=[DataRequired(), Length(min=10, max=255)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Submit Request')
